from __future__ import annotations

import json
import math
import os
import shutil
from pathlib import Path

import bpy
from mathutils import Vector
from PIL import Image

EXPERIMENT = "ocean-wave-bake"
SWEEP = os.environ.get("OCEAN_VARIANT_SWEEP", "0") == "1"
FAST_PREVIEW = os.environ.get("OCEAN_FAST_PREVIEW", "0") == "1"
VARIANT_ID = int(
    os.environ.get(
        "OCEAN_VARIANT",
        os.environ.get("EXPERIMENT_VARIANT", "0"),
    )
)
OUT = Path(os.environ.get("OCEAN_OUTPUT", "output52"))
FRAMES = OUT / "frames"

FRAME_START = 1
FRAME_END = 1 if SWEEP else (3 if FAST_PREVIEW else 24)
FPS = 24
RES_X = 320 if (SWEEP or FAST_PREVIEW) else 640
RES_Y = 180 if (SWEEP or FAST_PREVIEW) else 360
SAMPLES = 8 if (SWEEP or FAST_PREVIEW) else 24
GRID_N = 96 if SWEEP else 128
OCEAN_SIZE = 480.0
BAKE_SIZE = 256


def variant_config() -> dict:
    base = {
        "name": "baseline",
        "amplitude": 0.95,
        "wave_scale": 1.0,
        "chop": 0.35,
        "detail": 0.23,
        "water_color": (0.015, 0.075, 0.11, 1.0),
        "roughness": 0.13,
        "normal_strength": 0.58,
        "sun_energy": 4.0,
        "sun_angle": math.radians(24.0),
        "sun_rotation": math.radians(-32.0),
        "sun_color": (1.0, 0.92, 0.78),
        "sky_color": (0.22, 0.42, 0.62, 1.0),
        "sky_strength": 0.34,
        "camera": (0.0, -24.0, 4.6),
        "target": (0.0, 90.0, 1.1),
        "lens": 42.0,
    }
    variants = {
        1: {**base, "name": "calm-noon", "amplitude": 0.55, "wave_scale": 0.78, "detail": 0.16, "roughness": 0.10, "sun_angle": math.radians(42.0), "sky_color": (0.28, 0.52, 0.78, 1.0)},
        2: {**base, "name": "clear-teal", "water_color": (0.008, 0.10, 0.13, 1.0), "normal_strength": 0.72, "sun_angle": math.radians(32.0), "sky_color": (0.18, 0.44, 0.66, 1.0)},
        3: {**base, "name": "rough-wind", "amplitude": 1.35, "wave_scale": 1.35, "chop": 0.62, "detail": 0.38, "roughness": 0.18, "normal_strength": 0.85},
        4: {**base, "name": "storm-dark", "amplitude": 1.55, "wave_scale": 1.22, "chop": 0.70, "detail": 0.42, "water_color": (0.008, 0.025, 0.038, 1.0), "roughness": 0.21, "sun_energy": 1.4, "sun_color": (0.66, 0.72, 0.76), "sky_color": (0.055, 0.085, 0.11, 1.0), "sky_strength": 0.18},
        5: {**base, "name": "sunset-gold", "amplitude": 0.82, "wave_scale": 0.92, "water_color": (0.025, 0.060, 0.075, 1.0), "roughness": 0.12, "sun_energy": 5.0, "sun_angle": math.radians(8.0), "sun_rotation": math.radians(-58.0), "sun_color": (1.0, 0.48, 0.18), "sky_color": (0.34, 0.13, 0.12, 1.0), "sky_strength": 0.28},
        6: {**base, "name": "low-waterline", "camera": (0.0, -20.0, 2.0), "target": (0.0, 85.0, 0.6), "lens": 50.0, "amplitude": 1.05, "detail": 0.32},
        7: {**base, "name": "high-overview", "camera": (0.0, -28.0, 12.0), "target": (0.0, 75.0, -1.0), "lens": 48.0, "amplitude": 1.05, "wave_scale": 1.08},
        8: {**base, "name": "long-swell", "amplitude": 1.80, "wave_scale": 0.46, "chop": 0.20, "detail": 0.13, "normal_strength": 0.45, "camera": (0.0, -24.0, 4.0)},
        9: {**base, "name": "short-choppy", "amplitude": 0.72, "wave_scale": 1.90, "chop": 0.82, "detail": 0.62, "roughness": 0.20, "normal_strength": 1.0},
        10: {**base, "name": "grazing-reflection", "amplitude": 0.92, "wave_scale": 1.05, "roughness": 0.075, "normal_strength": 0.72, "sun_energy": 5.5, "sun_angle": math.radians(12.0), "sun_rotation": math.radians(-18.0), "sun_color": (1.0, 0.79, 0.48), "camera": (0.0, -24.0, 3.0), "target": (0.0, 90.0, 0.5), "lens": 55.0},
    }
    return variants.get(VARIANT_ID, base)


V = variant_config()


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.images,
    ):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def point_camera(camera: bpy.types.Object, target) -> None:
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def wave_height(x: float, y: float, t: float) -> float:
    s = V["wave_scale"]
    a = V["amplitude"]
    chop = V["chop"]
    components = (
        (0.050 * s, 0.0, 1.00, 0.80),
        (0.034 * s, 0.018 * s, 0.62, 1.08),
        (-0.022 * s, 0.043 * s, 0.38, 1.46),
        (0.075 * s, -0.036 * s, 0.17 + chop * 0.14, 2.25),
    )
    h = 0.0
    for kx, ky, weight, speed in components:
        h += weight * math.sin((x * kx + y * ky) * math.tau + t * speed * math.tau)
    detail = V["detail"]
    h += detail * math.sin((x * 0.28 * s - y * 0.19 * s) + t * math.tau * 2.4)
    h += detail * 0.55 * math.sin((x * 0.51 * s + y * 0.34 * s) - t * math.tau * 3.1)
    return a * h / 2.2


def generate_bake(frame: int) -> tuple[Path, Path]:
    bake_dir = OUT / "bake"
    bake_dir.mkdir(parents=True, exist_ok=True)
    height_path = bake_dir / f"height_{frame:04d}.png"
    normal_path = bake_dir / f"normal_{frame:04d}.png"
    t = (frame - FRAME_START) / max(1, FRAME_END - FRAME_START)
    n = BAKE_SIZE
    extent = 72.0
    heights = [[0.0] * n for _ in range(n)]
    maximum = max(0.01, V["amplitude"] * 1.4)

    for py in range(n):
        y = (py / (n - 1) - 0.5) * extent
        row = heights[py]
        for px in range(n):
            x = (px / (n - 1) - 0.5) * extent
            row[px] = wave_height(x, y, t)

    height_img = Image.new("L", (n, n))
    hp = height_img.load()
    for py in range(n):
        for px in range(n):
            v = 0.5 + 0.5 * max(-1.0, min(1.0, heights[py][px] / maximum))
            hp[px, py] = int(round(v * 255))
    height_img.save(height_path)

    normal_img = Image.new("RGB", (n, n))
    npix = normal_img.load()
    strength = 3.0 + V["normal_strength"] * 3.0
    for py in range(n):
        ym = max(0, py - 1)
        yp = min(n - 1, py + 1)
        for px in range(n):
            xm = max(0, px - 1)
            xp = min(n - 1, px + 1)
            dx = heights[py][xp] - heights[py][xm]
            dy = heights[yp][px] - heights[ym][px]
            nx, ny, nz = -dx * strength, -dy * strength, 1.0
            length = math.sqrt(nx * nx + ny * ny + nz * nz)
            nx, ny, nz = nx / length, ny / length, nz / length
            npix[px, py] = (
                int(round((nx * 0.5 + 0.5) * 255)),
                int(round((ny * 0.5 + 0.5) * 255)),
                int(round((nz * 0.5 + 0.5) * 255)),
            )
    normal_img.save(normal_path)
    return height_path, normal_path


def create_ocean_mesh(frame: int) -> bpy.types.Object:
    n = GRID_N
    half = OCEAN_SIZE * 0.5
    verts = []
    faces = []
    t = (frame - FRAME_START) / max(1, FRAME_END - FRAME_START)

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
    ocean = bpy.data.objects.new("OceanSurface", mesh)
    bpy.context.collection.objects.link(ocean)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    return ocean


def set_principled_input(bsdf, name: str, value) -> None:
    socket = bsdf.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def make_water_material(normal_path: Path):
    mat = bpy.data.materials.new("Baked-wave water")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    tex = nodes.new("ShaderNodeTexImage")
    normal = nodes.new("ShaderNodeNormalMap")

    image = bpy.data.images.load(str(normal_path.resolve()))
    try:
        image.colorspace_settings.name = "Non-Color"
    except Exception:
        pass
    tex.image = image
    tex.extension = "REPEAT"
    tex.interpolation = "Linear"
    normal.inputs["Strength"].default_value = V["normal_strength"]

    set_principled_input(bsdf, "Base Color", V["water_color"])
    set_principled_input(bsdf, "Roughness", V["roughness"])
    set_principled_input(bsdf, "IOR", 1.333)
    set_principled_input(bsdf, "Transmission Weight", 0.22)
    set_principled_input(bsdf, "Metallic", 0.0)

    links.new(tex.outputs["Color"], normal.inputs["Color"])
    links.new(normal.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def setup_world(scene: bpy.types.Scene) -> None:
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = V["sky_color"]
    bg.inputs["Strength"].default_value = V["sky_strength"]

    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, 20.0))
    sun = bpy.context.object
    sun.name = "OceanSun"
    sun.data.energy = V["sun_energy"]
    sun.data.color = V["sun_color"]
    sun.rotation_euler = (
        math.radians(55.0) - V["sun_angle"],
        V["sun_angle"],
        V["sun_rotation"],
    )
    sun.data.angle = math.radians(2.0)


def setup_camera(scene: bpy.types.Scene):
    bpy.ops.object.camera_add(location=V["camera"])
    camera = bpy.context.object
    camera.name = "OceanCamera"
    camera.data.lens = V["lens"]
    camera.data.sensor_width = 36.0
    camera.data.clip_end = 1000.0
    point_camera(camera, V["target"])
    scene.camera = camera
    return camera


def configure_scene(scene: bpy.types.Scene) -> None:
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    scene.render.fps = FPS
    scene.render.resolution_x = RES_X
    scene.render.resolution_y = RES_Y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = True
    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception as exc:
        print(f"COLOR_MANAGEMENT_FALLBACK={exc!r}")
    scene.view_settings.exposure = -0.1


def main() -> None:
    clear_scene()
    OUT.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)

    scene = bpy.context.scene
    configure_scene(scene)
    setup_world(scene)
    camera = setup_camera(scene)

    frame_stats = []
    ocean = None
    for frame in range(FRAME_START, FRAME_END + 1):
        height_path, normal_path = generate_bake(frame)
        if ocean is not None:
            bpy.data.objects.remove(ocean, do_unlink=True)

        ocean = create_ocean_mesh(frame)
        ocean.data.materials.append(make_water_material(normal_path))
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        scene.render.filepath = str(FRAMES / f"frame_{frame:04d}.png")
        bpy.ops.render.render(write_still=True)

        z_values = [v.co.z for v in ocean.data.vertices]
        frame_stats.append({
            "frame": frame,
            "min_z": round(float(min(z_values)), 4),
            "max_z": round(float(max(z_values)), 4),
            "height_bake": height_path.name,
            "normal_bake": normal_path.name,
        })

    preview_frame = 1 if SWEEP else (2 if FAST_PREVIEW else 12)
    shutil.copy2(FRAMES / f"frame_{preview_frame:04d}.png", OUT / "preview.png")

    report = {
        "experiment": EXPERIMENT,
        "source_video": "https://www.youtube.com/watch?v=qD6gM8Z2978",
        "reference_technique": "baked wave data applied as image texture",
        "variant_id": VARIANT_ID,
        "variant_name": V["name"],
        "variant_sweep": SWEEP,
        "fast_preview": FAST_PREVIEW,
        "blender_version": bpy.app.version_string,
        "engine": scene.render.engine,
        "device": "CPU",
        "samples": SAMPLES,
        "frame_count": FRAME_END - FRAME_START + 1,
        "fps": FPS,
        "resolution": [RES_X, RES_Y],
        "grid_n": GRID_N,
        "ocean_size_m": OCEAN_SIZE,
        "bake_size": BAKE_SIZE,
        "camera_lens_mm": float(camera.data.lens),
        "parameters": {
            "amplitude": V["amplitude"],
            "wave_scale": V["wave_scale"],
            "chop": V["chop"],
            "detail": V["detail"],
            "roughness": V["roughness"],
            "normal_strength": V["normal_strength"],
            "sun_energy": V["sun_energy"],
        },
        "frame_stats": frame_stats,
    }

    (OUT / f"{EXPERIMENT}-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    if not SWEEP and not FAST_PREVIEW:
        bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f"{EXPERIMENT}.blend"))

    print(f"OCEAN_VARIANT={VARIANT_ID}:{V['name']}")
    print(f"OCEAN_BAKE_SIZE={BAKE_SIZE}")
    print(f"OCEAN_GRID={GRID_N}x{GRID_N}")
    print(f"BLENDER52_VERSION={bpy.app.version_string}")
    print(f"BLENDER52_ENGINE={scene.render.engine}")
    print(f"BLENDER52_FRAMES={report['frame_count']}")


if __name__ == "__main__":
    main()
