from __future__ import annotations

import json
import math
import random
import shutil
from pathlib import Path

import bpy
from mathutils import Vector

OUT = Path("output52")
FRAMES = OUT / "frames"
EXPERIMENT = "tropical-resort-coast-still"
RES_X = 960
RES_Y = 540
SAMPLES = 32
FRAME = 1


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def set_input(node, name: str, value) -> None:
    socket = node.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def point_camera(camera: bpy.types.Object, target) -> None:
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def shoreline_y(x: float) -> float:
    # A diagonal, gently irregular shoreline reads as a coast rather than stacked bands.
    return -10.0 + 0.22 * x + 7.0 * math.sin(x * 0.014) + 2.2 * math.sin(x * 0.051)


def seabed_z(x: float, y: float) -> float:
    yp = y - shoreline_y(x)
    if yp < -18.0:
        z = 0.55 + (-18.0 - yp) * 0.020
    elif yp < 22.0:
        z = 0.55 - (yp + 18.0) * 0.030
    elif yp < 350.0:
        z = -0.65 - (yp - 22.0) * 0.0060
    elif yp < 850.0:
        z = -2.618 - (yp - 350.0) * 0.0060
    else:
        z = -5.618 - (yp - 850.0) * 0.0040

    ripple = 0.050 * math.sin(x * 0.42 + y * 0.11)
    ripple += 0.026 * math.sin(x * 0.71 - y * 0.19)
    ripple *= math.exp(-max(0.0, yp) / 230.0)
    dune = 0.075 * math.sin(x * 0.055 + y * 0.022) * math.exp(-max(0.0, yp) / 350.0)
    return z + ripple + dune


def make_sand_material(
    name: str,
    base: tuple[float, float, float, float],
    roughness: float,
    bump_strength: float,
    coat: float = 0.0,
):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    noise = nodes.new("ShaderNodeTexNoise")
    ramp = nodes.new("ShaderNodeValToRGB")
    bump = nodes.new("ShaderNodeBump")
    coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")

    noise.noise_dimensions = "3D"
    set_input(noise, "Scale", 6.0)
    set_input(noise, "Detail", 4.5)
    set_input(noise, "Roughness", 0.72)
    set_input(noise, "Distortion", 0.18)

    mapping.inputs["Scale"].default_value = (7.0, 7.0, 7.0)

    lo = tuple(max(0.0, c * 0.74) for c in base[:3]) + (1.0,)
    hi = tuple(min(1.0, c * 1.12 + 0.025) for c in base[:3]) + (1.0,)
    ramp.color_ramp.elements[0].position = 0.26
    ramp.color_ramp.elements[0].color = lo
    ramp.color_ramp.elements[1].position = 0.78
    ramp.color_ramp.elements[1].color = hi

    set_input(bsdf, "Roughness", roughness)
    set_input(bsdf, "Metallic", 0.0)
    set_input(bsdf, "Coat Weight", coat)
    set_input(bsdf, "Coat Roughness", max(0.03, roughness * 0.35))
    set_input(bump, "Strength", bump_strength)
    set_input(bump, "Distance", 0.08)

    links.new(coord.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def make_underwater_sand_material():
    mat = bpy.data.materials.new("Underwater pale sand + caustics")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    vor = nodes.new("ShaderNodeTexVoronoi")
    ramp = nodes.new("ShaderNodeValToRGB")
    noise = nodes.new("ShaderNodeTexNoise")
    bump = nodes.new("ShaderNodeBump")

    mapping.inputs["Scale"].default_value = (72.0, 110.0, 4.0)
    vor.feature = "DISTANCE_TO_EDGE"
    vor.distance = "EUCLIDEAN"
    set_input(vor, "Scale", 1.0)

    ramp.color_ramp.elements[0].position = 0.018
    ramp.color_ramp.elements[0].color = (1.0, 0.88, 0.55, 1.0)
    ramp.color_ramp.elements[1].position = 0.085
    ramp.color_ramp.elements[1].color = (0.38, 0.34, 0.23, 1.0)

    noise.noise_dimensions = "3D"
    set_input(noise, "Scale", 18.0)
    set_input(noise, "Detail", 4.0)
    set_input(noise, "Roughness", 0.62)
    set_input(bump, "Strength", 0.16)
    set_input(bump, "Distance", 0.035)

    set_input(bsdf, "Roughness", 0.58)
    set_input(bsdf, "Metallic", 0.0)

    links.new(coord.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], vor.inputs["Vector"])
    links.new(vor.outputs["Distance"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(coord.outputs["Generated"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def create_beach() -> bpy.types.Object:
    nx = 156
    ny = 300
    xmin, xmax = -240.0, 240.0
    ymin, ymax = -110.0, 700.0

    verts = []
    faces = []
    for iy in range(ny):
        y = ymin + (ymax - ymin) * iy / (ny - 1)
        for ix in range(nx):
            x = xmin + (xmax - xmin) * ix / (nx - 1)
            verts.append((x, y, seabed_z(x, y)))

    for iy in range(ny - 1):
        for ix in range(nx - 1):
            a = iy * nx + ix
            faces.append((a, a + 1, a + nx + 1, a + nx))

    mesh = bpy.data.meshes.new("BeachAndSeabedMesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    beach = bpy.data.objects.new("BeachAndSeabed", mesh)
    bpy.context.collection.objects.link(beach)

    dry = make_sand_material("Dry white coral sand", (0.68, 0.62, 0.50, 1.0), 0.78, 0.14)
    wet = make_sand_material("Wet compact sand", (0.28, 0.24, 0.18, 1.0), 0.22, 0.08, coat=0.14)
    underwater = make_underwater_sand_material()
    beach.data.materials.append(dry)
    beach.data.materials.append(wet)
    beach.data.materials.append(underwater)

    for poly in mesh.polygons:
        center = sum((mesh.vertices[i].co for i in poly.vertices), Vector()) / len(poly.vertices)
        yp = center.y - shoreline_y(center.x)
        if yp < -5.5:
            poly.material_index = 0
        elif yp < 3.5:
            poly.material_index = 1
        else:
            poly.material_index = 2

    for poly in mesh.polygons:
        poly.use_smooth = True
    return beach


def make_simple_material(name: str, color, roughness: float = 0.6):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    set_input(bsdf, "Base Color", color)
    set_input(bsdf, "Roughness", roughness)
    return mat


def create_reef_patches() -> int:
    rng = random.Random(11)
    mats = [
        make_simple_material("Reef olive", (0.055, 0.085, 0.055, 1.0), 0.86),
        make_simple_material("Reef brown", (0.11, 0.075, 0.045, 1.0), 0.84),
        make_simple_material("Sea grass dark", (0.028, 0.075, 0.055, 1.0), 0.90),
    ]
    count = 0
    for _ in range(42):
        x = rng.uniform(-175.0, 175.0)
        y = rng.uniform(38.0, 650.0)
        if rng.random() < 0.35 and y < 75.0:
            continue
        z = seabed_z(x, y) + 0.035
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0, location=(x, y, z))
        patch = bpy.context.object
        patch.name = f"ReefPatch_{count:02d}"
        patch.scale = (rng.uniform(2.2, 7.5), rng.uniform(1.6, 5.2), rng.uniform(0.05, 0.16))
        patch.rotation_euler[2] = rng.uniform(0.0, math.tau)
        patch.data.materials.append(mats[count % len(mats)])
        count += 1
    return count


def make_water_surface_material():
    mat = bpy.data.materials.new("LagoonWaterSurface")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    coord = nodes.new("ShaderNodeTexCoord")
    separate = nodes.new("ShaderNodeSeparateXYZ")
    depth_ramp = nodes.new("ShaderNodeValToRGB")
    transmission = nodes.new("ShaderNodeMapRange")
    noise_a = nodes.new("ShaderNodeTexNoise")
    noise_b = nodes.new("ShaderNodeTexNoise")
    bump_a = nodes.new("ShaderNodeBump")
    bump_b = nodes.new("ShaderNodeBump")

    cr = depth_ramp.color_ramp
    cr.elements[0].position = 0.00
    cr.elements[0].color = (0.22, 0.72, 0.68, 1.0)
    mid = cr.elements.new(0.54)
    mid.color = (0.045, 0.48, 0.55, 1.0)
    cr.elements[1].position = 1.00
    cr.elements[1].color = (0.025, 0.23, 0.34, 1.0)

    transmission.inputs["From Min"].default_value = 0.0
    transmission.inputs["From Max"].default_value = 1.0
    transmission.inputs["To Min"].default_value = 0.985
    transmission.inputs["To Max"].default_value = 0.82
    transmission.clamp = True

    noise_a.noise_dimensions = "3D"
    set_input(noise_a, "Scale", 9.0)
    set_input(noise_a, "Detail", 5.0)
    set_input(noise_a, "Roughness", 0.64)

    noise_b.noise_dimensions = "3D"
    set_input(noise_b, "Scale", 42.0)
    set_input(noise_b, "Detail", 3.0)
    set_input(noise_b, "Roughness", 0.56)

    set_input(bump_a, "Strength", 0.20)
    set_input(bump_a, "Distance", 0.10)
    set_input(bump_b, "Strength", 0.10)
    set_input(bump_b, "Distance", 0.020)

    set_input(bsdf, "Roughness", 0.032)
    set_input(bsdf, "IOR", 1.333)
    set_input(bsdf, "Metallic", 0.0)
    set_input(bsdf, "Coat Weight", 0.03)
    set_input(bsdf, "Coat Roughness", 0.02)

    links.new(coord.outputs["Generated"], separate.inputs["Vector"])
    links.new(separate.outputs["Y"], depth_ramp.inputs["Fac"])
    links.new(separate.outputs["Y"], transmission.inputs["Value"])
    links.new(depth_ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(transmission.outputs["Result"], bsdf.inputs["Transmission Weight"])

    links.new(coord.outputs["Generated"], noise_a.inputs["Vector"])
    links.new(coord.outputs["Generated"], noise_b.inputs["Vector"])
    links.new(noise_a.outputs["Fac"], bump_a.inputs["Height"])
    links.new(noise_b.outputs["Fac"], bump_b.inputs["Height"])
    links.new(bump_a.outputs["Normal"], bump_b.inputs["Normal"])
    links.new(bump_b.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def create_ocean() -> tuple[bpy.types.Object, dict]:
    nx = 180
    ny = 260
    xmin, xmax = -280.0, 280.0
    far_y = 1450.0

    verts = []
    faces = []
    for iy in range(ny):
        t = iy / (ny - 1)
        t_space = t ** 1.30
        for ix in range(nx):
            x = xmin + (xmax - xmin) * ix / (nx - 1)
            shore = shoreline_y(x) + 0.45
            y = shore + (far_y - shore) * t_space

            offshore = min(1.0, t * 1.65)
            amp = 0.010 + 0.135 * offshore
            long_wave = math.sin(x * 0.044 + y * 0.024)
            cross_wave = math.sin(-x * 0.031 + y * 0.047 + 1.7)
            detail = math.sin(x * 0.16 + y * 0.12 + 0.8)
            z = amp * (0.56 * long_wave + 0.30 * cross_wave + 0.14 * detail)
            verts.append((x, y, z))

    for iy in range(ny - 1):
        for ix in range(nx - 1):
            a = iy * nx + ix
            faces.append((a, a + 1, a + nx + 1, a + nx))

    mesh = bpy.data.meshes.new("ShorelineFollowingWaterMesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    ocean = bpy.data.objects.new("ShorelineFollowingWater", mesh)
    bpy.context.collection.objects.link(ocean)
    ocean.data.materials.append(make_water_surface_material())
    for poly in mesh.polygons:
        poly.use_smooth = True

    settings = {
        "spectrum": "SHORELINE_GERSTNER_PROXY",
        "shoreline_following": True,
        "grid": [nx, ny],
        "far_y_m": far_y,
        "max_wave_amplitude_m": 0.145,
        "ior": 1.333,
        "depth_tint": "three-stop generated-Y lagoon gradient",
        "transmission_range": [0.985, 0.82],
    }
    return ocean, settings


def make_water_volume_material():
    return None


def create_water_volume():
    return None


def create_foam() -> int:
    rng = random.Random(29)
    verts = []
    faces = []
    fragment_count = 0

    bands = (
        (0.65, 0.72, 0.12, 0.34),
        (3.4, 0.36, 0.07, 0.20),
    )
    for band_index, (offset, chance, width_min, width_max) in enumerate(bands):
        x = -205.0 + rng.uniform(0.0, 4.0)
        while x < 205.0:
            seg_len = rng.uniform(2.2, 7.5)
            gap = rng.uniform(1.0, 5.0)
            if rng.random() < chance:
                steps = 9
                base = len(verts)
                width0 = rng.uniform(width_min, width_max)
                phase = rng.uniform(0.0, math.tau)
                for i in range(steps):
                    u = i / (steps - 1)
                    px = x + seg_len * u
                    py = shoreline_y(px) + offset
                    py += 0.26 * math.sin(px * 0.16 + phase)
                    width = width0 * (0.48 + 0.52 * math.sin(math.pi * u))
                    z = 0.040 + 0.010 * band_index
                    verts.append((px, py - width, z))
                    verts.append((px, py + width, z))
                for i in range(steps - 1):
                    a = base + i * 2
                    faces.append((a, a + 2, a + 3, a + 1))
                fragment_count += 1
            x += seg_len + gap

    mesh = bpy.data.meshes.new("FoamRibbonMesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    foam = bpy.data.objects.new("ShorelineFoam", mesh)
    bpy.context.collection.objects.link(foam)

    mat = bpy.data.materials.new("Thin shoreline foam")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    set_input(bsdf, "Base Color", (0.93, 0.97, 0.95, 1.0))
    set_input(bsdf, "Roughness", 0.30)
    set_input(bsdf, "Transmission Weight", 0.10)
    foam.data.materials.append(mat)
    return fragment_count


def setup_world_and_light(scene: bpy.types.Scene) -> str:
    world = scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputWorld")
    bg = nodes.new("ShaderNodeBackground")
    sky = nodes.new("ShaderNodeTexSky")
    sky_model = "UNKNOWN"

    for candidate in ("MULTIPLE_SCATTERING", "NISHITA"):
        try:
            sky.sky_type = candidate
            sky_model = candidate
            break
        except Exception:
            continue

    for attr, value in (
        ("sun_elevation", math.radians(54.0)),
        ("sun_rotation", math.radians(122.0)),
        ("altitude", 12.0),
        ("air_density", 1.0),
        ("dust_density", 0.62),
        ("ozone_density", 1.0),
    ):
        if hasattr(sky, attr):
            setattr(sky, attr, value)

    bg.inputs["Strength"].default_value = 0.20
    links.new(sky.outputs["Color"], bg.inputs["Color"])
    links.new(bg.outputs["Background"], out.inputs["Surface"])

    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, 40.0))
    sun = bpy.context.object
    sun.name = "TropicalNoonSun"
    sun.data.energy = 1.65
    sun.data.angle = math.radians(0.75)
    sun.rotation_euler = (math.radians(28.0), math.radians(-12.0), math.radians(-38.0))
    return sky_model


def setup_camera(scene: bpy.types.Scene) -> bpy.types.Object:
    bpy.ops.object.camera_add(location=(58.0, -120.0, 18.0))
    camera = bpy.context.object
    camera.name = "ResortCoastCamera"
    camera.data.lens = 50.0
    camera.data.sensor_width = 36.0
    camera.data.clip_start = 0.1
    camera.data.clip_end = 2500.0
    point_camera(camera, (-18.0, 112.0, -1.2))
    scene.camera = camera
    return camera


def configure_render(scene: bpy.types.Scene) -> None:
    scene.frame_start = FRAME
    scene.frame_end = FRAME
    scene.render.fps = 24
    scene.render.resolution_x = RES_X
    scene.render.resolution_y = RES_Y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 8
    scene.cycles.transmission_bounces = 6
    scene.cycles.volume_bounces = 1
    scene.cycles.transparent_max_bounces = 6

    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception as exc:
        print(f"COLOR_MANAGEMENT_FALLBACK={exc!r}")
    scene.view_settings.exposure = -1.10


def main() -> None:
    clear_scene()
    OUT.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)

    scene = bpy.context.scene
    configure_render(scene)
    sky_model = setup_world_and_light(scene)
    camera = setup_camera(scene)

    beach = create_beach()
    reef_count = create_reef_patches()
    ocean, ocean_settings = create_ocean()
    volume = create_water_volume()
    foam_count = create_foam()

    scene.frame_set(FRAME)
    bpy.context.view_layer.update()
    frame_path = FRAMES / "frame_0001.png"
    scene.render.filepath = str(frame_path)
    bpy.ops.render.render(write_still=True)
    shutil.copy2(frame_path, OUT / "preview.png")

    report = {
        "experiment": EXPERIMENT,
        "blender_version": bpy.app.version_string,
        "engine": scene.render.engine,
        "device": "CPU",
        "frame_count": 1,
        "resolution": [RES_X, RES_Y],
        "samples": SAMPLES,
        "still_only": True,
        "camera": {
            "location": [round(float(v), 4) for v in camera.location],
            "lens_mm": float(camera.data.lens),
        },
        "ocean": ocean_settings,
        "water_model": {
            "surface": "Principled transmission, IOR 1.333, two-scale procedural normals",
            "volume": "disabled in pass 3; depth cue comes from transmissive surface tint and seabed",
        },
        "shore": {
            "wet_sand_material": True,
            "foam_patch_count": foam_count,
            "reef_patch_count": reef_count,
        },
        "objects": {
            "beach": beach.name,
            "ocean": ocean.name,
            "water_volume": None,
        },
        "sky_model": sky_model,
        "color_management": scene.view_settings.view_transform,
    }
    (OUT / f"{EXPERIMENT}-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f"{EXPERIMENT}.blend"))

    print(f"TROPICAL_COAST_ENGINE={scene.render.engine}")
    print(f"TROPICAL_COAST_SPECTRUM={ocean_settings['spectrum']}")
    print(f"TROPICAL_COAST_SAMPLES={SAMPLES}")
    print(f"TROPICAL_COAST_RESOLUTION={RES_X}x{RES_Y}")
    print(f"TROPICAL_COAST_SKY={sky_model}")


if __name__ == "__main__":
    main()
