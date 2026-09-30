from __future__ import annotations

import json
import math
import os
import shutil
from pathlib import Path

import bpy
from mathutils import Vector

EXPERIMENT = "ocean-ship-float"
VARIANT_ID = int(os.environ.get("SHIP_VARIANT", "1"))
SWEEP = os.environ.get("SHIP_VARIANT_SWEEP", "0") == "1"
OUT = Path(os.environ.get("SHIP_OUTPUT", "output52"))
FRAMES = OUT / "frames"

FRAME_START = 1
FRAME_END = 1 if SWEEP else 3
FPS = 24
RES_X = 320
RES_Y = 180
SAMPLES = 8
GRID_N = 96
OCEAN_SIZE = 300.0
BAKE_SIZE = 192
SHIP_LENGTH_M = 18.0
SHIP_X = 9.0
SHIP_Y = -3.0

ASSET = Path("assets/ships/quaternius-sail-ship/Sail ship.obj")


def variant_config() -> dict:
    base = {
        "name": "height-follow",
        "heave": 1.0,
        "tilt": 0.0,
        "draft_fraction": 0.18,
        "amplitude": 0.85,
        "wave_scale": 0.72,
        "detail": 0.20,
        "roughness": 0.12,
        "normal_strength": 0.55,
        "camera": (30.0, -42.0, 10.0),
        "target_z": 5.0,
        "lens": 52.0,
        "sun_energy": 4.2,
    }
    variants = {
        1: {**base, "name": "fixed-reference", "heave": 0.0, "tilt": 0.0},
        2: {**base, "name": "height-follow"},
        3: {**base, "name": "gentle-float", "tilt": 0.42},
        4: {**base, "name": "full-float", "tilt": 0.85},
        5: {
            **base,
            "name": "long-swell-low-camera",
            "tilt": 0.60,
            "amplitude": 1.20,
            "wave_scale": 0.48,
            "detail": 0.13,
            "camera": (27.0, -38.0, 5.2),
            "target_z": 4.0,
            "lens": 58.0,
        },
        6: {
            **base,
            "name": "rough-sea",
            "tilt": 0.72,
            "amplitude": 1.10,
            "wave_scale": 1.28,
            "detail": 0.42,
            "roughness": 0.17,
            "normal_strength": 0.82,
            "camera": (32.0, -46.0, 8.0),
            "target_z": 4.8,
        },
    }
    return variants.get(VARIANT_ID, base)


V = variant_config()


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for blocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.images,
    ):
        for block in list(blocks):
            if block.users == 0:
                blocks.remove(block)


def point_camera(camera: bpy.types.Object, target) -> None:
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def wave_height(x: float, y: float, t: float) -> float:
    s = V["wave_scale"]
    a = V["amplitude"]
    h = 0.0
    for kx, ky, weight, speed in (
        (0.040 * s, 0.006 * s, 1.00, 0.62),
        (0.024 * s, 0.027 * s, 0.58, 0.91),
        (-0.018 * s, 0.036 * s, 0.36, 1.22),
        (0.072 * s, -0.031 * s, 0.18, 1.80),
    ):
        h += weight * math.sin((x * kx + y * ky) * math.tau + t * speed * math.tau)
    d = V["detail"]
    h += d * math.sin(x * 0.25 * s - y * 0.16 * s + t * math.tau * 2.2)
    h += d * 0.45 * math.sin(x * 0.43 * s + y * 0.29 * s - t * math.tau * 2.7)
    return a * h / 2.15


def save_image(name: str, path: Path, width: int, height: int, pixels) -> bpy.types.Image:
    old = bpy.data.images.get(name)
    if old is not None:
        bpy.data.images.remove(old)
    image = bpy.data.images.new(name, width=width, height=height, alpha=False)
    image.pixels.foreach_set(pixels)
    image.filepath_raw = str(path.resolve())
    image.file_format = "PNG"
    image.save()
    return image


def generate_normal_bake(frame: int) -> Path:
    bake_dir = OUT / "bake"
    bake_dir.mkdir(parents=True, exist_ok=True)
    path = bake_dir / f"normal_{frame:04d}.png"
    n = BAKE_SIZE
    extent = 68.0
    t = (frame - FRAME_START) / max(1, FRAME_END - FRAME_START)
    heights = [[0.0] * n for _ in range(n)]
    for py in range(n):
        y = (py / (n - 1) - 0.5) * extent
        for px in range(n):
            x = (px / (n - 1) - 0.5) * extent
            heights[py][px] = wave_height(x, y, t)

    pixels = [0.0] * (n * n * 4)
    strength = 3.0 + V["normal_strength"] * 3.0
    for py in range(n):
        ym, yp = max(0, py - 1), min(n - 1, py + 1)
        for px in range(n):
            xm, xp = max(0, px - 1), min(n - 1, px + 1)
            dx = heights[py][xp] - heights[py][xm]
            dy = heights[yp][px] - heights[ym][px]
            nx, ny, nz = -dx * strength, -dy * strength, 1.0
            mag = math.sqrt(nx * nx + ny * ny + nz * nz)
            idx = (py * n + px) * 4
            pixels[idx:idx + 4] = (
                nx / mag * 0.5 + 0.5,
                ny / mag * 0.5 + 0.5,
                nz / mag * 0.5 + 0.5,
                1.0,
            )
    image = save_image(f"OceanNormal_{frame:04d}", path, n, n, pixels)
    try:
        image.colorspace_settings.name = "Non-Color"
    except Exception:
        pass
    return path


def create_ocean(frame: int) -> bpy.types.Object:
    n = GRID_N
    half = OCEAN_SIZE * 0.5
    t = (frame - FRAME_START) / max(1, FRAME_END - FRAME_START)
    verts = []
    faces = []
    for iy in range(n):
        y = -half + OCEAN_SIZE * iy / (n - 1)
        for ix in range(n):
            x = -half + OCEAN_SIZE * ix / (n - 1)
            verts.append((x, y, wave_height(x, y, t)))
    for iy in range(n - 1):
        for ix in range(n - 1):
            a = iy * n + ix
            faces.append((a, a + 1, a + n + 1, a + n))
    mesh = bpy.data.meshes.new("OceanMesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("OceanSurface", mesh)
    bpy.context.collection.objects.link(obj)
    for p in mesh.polygons:
        p.use_smooth = True
    return obj


def water_material(normal_path: Path):
    mat = bpy.data.materials.new("Baked Ocean Water")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    tex = nodes.new("ShaderNodeTexImage")
    normal = nodes.new("ShaderNodeNormalMap")
    image = bpy.data.images.load(str(normal_path.resolve()))
    try:
        image.colorspace_settings.name = "Non-Color"
    except Exception:
        pass
    tex.image = image
    tex.extension = "REPEAT"
    mapping.inputs["Scale"].default_value = (8.0, 8.0, 8.0)
    normal.inputs["Strength"].default_value = V["normal_strength"]
    bsdf.inputs["Base Color"].default_value = (0.012, 0.065, 0.095, 1.0)
    bsdf.inputs["Roughness"].default_value = V["roughness"]
    if bsdf.inputs.get("IOR"):
        bsdf.inputs["IOR"].default_value = 1.333
    if bsdf.inputs.get("Transmission Weight"):
        bsdf.inputs["Transmission Weight"].default_value = 0.16
    links.new(coord.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
    links.new(tex.outputs["Color"], normal.inputs["Color"])
    links.new(normal.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def bbox_world(objects):
    points = []
    for obj in objects:
        for corner in obj.bound_box:
            points.append(obj.matrix_world @ Vector(corner))
    mins = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maxs = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return mins, maxs


def import_ship():
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=str(ASSET.resolve()))
    imported = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    if not imported:
        raise RuntimeError("OBJ import produced no mesh objects")

    root = bpy.data.objects.new("ShipRoot", None)
    bpy.context.collection.objects.link(root)
    for obj in imported:
        matrix = obj.matrix_world.copy()
        obj.parent = root
        obj.matrix_world = matrix

    bpy.context.view_layer.update()
    mins, maxs = bbox_world(imported)
    dims = maxs - mins
    horizontal_length = max(dims.x, dims.y)
    scale = SHIP_LENGTH_M / max(0.001, horizontal_length)
    root.scale = (scale, scale, scale)
    bpy.context.view_layer.update()

    mins, maxs = bbox_world(imported)
    center = (mins + maxs) * 0.5
    root.location.x += SHIP_X - center.x
    root.location.y += SHIP_Y - center.y
    bpy.context.view_layer.update()

    mins, maxs = bbox_world(imported)
    hulls = [o for o in imported if "bigship" in o.name.lower()]
    hull_mins, hull_maxs = bbox_world(hulls or imported)
    waterline = hull_mins.z + (hull_maxs.z - hull_mins.z) * V["draft_fraction"]
    root.location.z -= waterline
    bpy.context.view_layer.update()

    mins, maxs = bbox_world(imported)
    dims = maxs - mins
    root["forward_axis"] = "X" if dims.x >= dims.y else "Y"
    return root, imported, mins, maxs, dims


def update_ship(root, frame: int, dims) -> dict:
    t = (frame - FRAME_START) / max(1, FRAME_END - FRAME_START)
    cx, cy = SHIP_X, SHIP_Y
    center_h = wave_height(cx, cy, t)
    root.location.z = center_h * V["heave"] + root.get("base_z", root.location.z)

    probe_x = max(2.0, dims.x * 0.28)
    probe_y = max(2.0, dims.y * 0.28)
    hx1 = wave_height(cx + probe_x, cy, t)
    hx0 = wave_height(cx - probe_x, cy, t)
    hy1 = wave_height(cx, cy + probe_y, t)
    hy0 = wave_height(cx, cy - probe_y, t)
    slope_x = math.atan2(hx1 - hx0, probe_x * 2.0)
    slope_y = math.atan2(hy1 - hy0, probe_y * 2.0)

    root.rotation_euler.x = slope_y * V["tilt"]
    root.rotation_euler.y = -slope_x * V["tilt"]
    root.rotation_euler.z = math.radians(-12.0)
    return {
        "center_wave": round(center_h, 4),
        "rot_x_deg": round(math.degrees(root.rotation_euler.x), 3),
        "rot_y_deg": round(math.degrees(root.rotation_euler.y), 3),
    }


def setup_scene():
    clear_scene()
    scene = bpy.context.scene
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    scene.render.fps = FPS
    scene.render.resolution_x = RES_X
    scene.render.resolution_y = RES_Y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = True
    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass

    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.18, 0.39, 0.62, 1.0)
    bg.inputs["Strength"].default_value = 0.34

    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, 30.0))
    sun = bpy.context.object
    sun.data.energy = V["sun_energy"]
    sun.data.color = (1.0, 0.92, 0.78)
    sun.rotation_euler = (math.radians(35), math.radians(18), math.radians(-35))
    sun.data.angle = math.radians(2.0)

    root, meshes, mins, maxs, dims = import_ship()
    root["base_z"] = root.location.z

    bpy.ops.object.camera_add(location=V["camera"])
    camera = bpy.context.object
    camera.data.lens = V["lens"]
    camera.data.sensor_width = 36.0
    camera.data.clip_end = 1000.0
    point_camera(camera, (SHIP_X, SHIP_Y + 5.0, V["target_z"]))
    scene.camera = camera

    return scene, camera, root, meshes, dims


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)
    scene, camera, root, ship_meshes, ship_dims = setup_scene()

    frame_stats = []
    ocean = None
    for frame in range(FRAME_START, FRAME_END + 1):
        if ocean is not None:
            bpy.data.objects.remove(ocean, do_unlink=True)
        normal_path = generate_normal_bake(frame)
        ocean = create_ocean(frame)
        ocean.data.materials.append(water_material(normal_path))
        ship_stat = update_ship(root, frame, ship_dims)

        scene.frame_set(frame)
        bpy.context.view_layer.update()
        scene.render.filepath = str(FRAMES / f"frame_{frame:04d}.png")
        bpy.ops.render.render(write_still=True)
        frame_stats.append({"frame": frame, **ship_stat})

    shutil.copy2(FRAMES / "frame_0001.png", OUT / "preview.png")
    mins, maxs = bbox_world(ship_meshes)
    report = {
        "experiment": EXPERIMENT,
        "variant_id": VARIANT_ID,
        "variant_name": V["name"],
        "source_asset": "Quaternius Ships Pack / Sail ship",
        "asset_license": "CC0",
        "blender_version": bpy.app.version_string,
        "engine": scene.render.engine,
        "resolution": [RES_X, RES_Y],
        "frame_count": FRAME_END - FRAME_START + 1,
        "ship_mesh_count": len(ship_meshes),
        "ship_object_names": [o.name for o in ship_meshes],
        "ship_bbox_min": [round(float(v), 4) for v in mins],
        "ship_bbox_max": [round(float(v), 4) for v in maxs],
        "ship_dimensions": [round(float(v), 4) for v in (maxs - mins)],
        "ship_target_length_m": SHIP_LENGTH_M,
        "float": {
            "heave_response": V["heave"],
            "tilt_response": V["tilt"],
            "draft_fraction": V["draft_fraction"],
        },
        "ocean": {
            "amplitude": V["amplitude"],
            "wave_scale": V["wave_scale"],
            "detail": V["detail"],
        },
        "frame_stats": frame_stats,
    }
    (OUT / f"{EXPERIMENT}-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
