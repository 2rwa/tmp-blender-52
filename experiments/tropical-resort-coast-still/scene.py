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
    return 0.025 * x + 4.0 * math.sin(x * 0.018) + 1.3 * math.sin(x * 0.061)


def seabed_z(x: float, y: float) -> float:
    yp = y - shoreline_y(x)
    if yp < -18.0:
        z = 0.55 + (-18.0 - yp) * 0.020
    elif yp < 22.0:
        z = 0.55 - (yp + 18.0) * 0.030
    else:
        z = -0.65 - (yp - 22.0) * 0.021

    ripple = 0.035 * math.sin(x * 0.42 + y * 0.11)
    ripple += 0.020 * math.sin(x * 0.71 - y * 0.19)
    ripple *= math.exp(-max(0.0, yp) / 110.0)
    dune = 0.055 * math.sin(x * 0.055 + y * 0.022) * math.exp(-max(0.0, yp) / 160.0)
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


def create_beach() -> bpy.types.Object:
    nx = 128
    ny = 196
    xmin, xmax = -170.0, 170.0
    ymin, ymax = -90.0, 360.0

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

    dry = make_sand_material("Dry white coral sand", (0.77, 0.69, 0.53, 1.0), 0.82, 0.17)
    wet = make_sand_material("Wet compact sand", (0.34, 0.29, 0.20, 1.0), 0.26, 0.10, coat=0.10)
    underwater = make_sand_material("Underwater pale sand", (0.69, 0.62, 0.45, 1.0), 0.68, 0.12)
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
    for _ in range(28):
        x = rng.uniform(-135.0, 135.0)
        y = rng.uniform(38.0, 260.0)
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
    noise_a = nodes.new("ShaderNodeTexNoise")
    noise_b = nodes.new("ShaderNodeTexNoise")
    bump_a = nodes.new("ShaderNodeBump")
    bump_b = nodes.new("ShaderNodeBump")
    coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")

    mapping.inputs["Scale"].default_value = (0.24, 0.24, 0.24)
    set_input(noise_a, "Scale", 3.2)
    set_input(noise_a, "Detail", 4.0)
    set_input(noise_a, "Roughness", 0.62)
    set_input(noise_b, "Scale", 14.0)
    set_input(noise_b, "Detail", 2.4)
    set_input(noise_b, "Roughness", 0.58)

    set_input(bump_a, "Strength", 0.18)
    set_input(bump_a, "Distance", 0.20)
    set_input(bump_b, "Strength", 0.10)
    set_input(bump_b, "Distance", 0.055)

    set_input(bsdf, "Base Color", (0.80, 0.93, 0.97, 1.0))
    set_input(bsdf, "Roughness", 0.035)
    set_input(bsdf, "IOR", 1.333)
    set_input(bsdf, "Transmission Weight", 1.0)
    set_input(bsdf, "Metallic", 0.0)

    links.new(coord.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise_a.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise_b.inputs["Vector"])
    links.new(noise_a.outputs["Fac"], bump_a.inputs["Height"])
    links.new(noise_b.outputs["Fac"], bump_b.inputs["Height"])
    links.new(bump_a.outputs["Normal"], bump_b.inputs["Normal"])
    links.new(bump_b.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def create_ocean() -> tuple[bpy.types.Object, dict]:
    bpy.ops.mesh.primitive_plane_add(size=2.0, location=(0.0, 280.0, 0.0))
    ocean = bpy.context.object
    ocean.name = "TMA_Shallow_Lagoon"
    ocean.data.materials.append(make_water_surface_material())

    mod = ocean.modifiers.new("TMA shallow-water spectrum", "OCEAN")
    if hasattr(mod, "geometry_mode"):
        mod.geometry_mode = "GENERATE"
    mod.spectrum = "TEXEL_MARSEN_ARSLOE"
    mod.resolution = 8
    mod.viewport_resolution = 6
    mod.spatial_size = 350
    mod.repeat_x = 2
    mod.repeat_y = 4
    mod.depth = 4.0
    mod.wave_scale = 0.22
    mod.wave_scale_min = 0.22
    mod.choppiness = 0.33
    mod.wind_velocity = 3.8
    mod.wave_alignment = 0.82
    mod.wave_direction = math.radians(86.0)
    mod.damping = 0.82
    mod.random_seed = 17
    mod.time = 1.15
    mod.use_normals = True
    if hasattr(mod, "sharpen_peak_jonswap"):
        mod.sharpen_peak_jonswap = 0.12
    if hasattr(mod, "fetch_jonswap"):
        mod.fetch_jonswap = 48.0

    settings = {
        "spectrum": mod.spectrum,
        "depth_m": float(mod.depth),
        "wind_velocity_m_s": float(mod.wind_velocity),
        "wave_scale": float(mod.wave_scale),
        "choppiness": float(mod.choppiness),
        "alignment": float(mod.wave_alignment),
        "spatial_size_m": int(mod.spatial_size),
        "repeat": [int(mod.repeat_x), int(mod.repeat_y)],
        "resolution": int(mod.resolution),
    }
    return ocean, settings


def make_water_volume_material():
    mat = bpy.data.materials.new("LagoonWaterVolume")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    absorption = nodes.new("ShaderNodeVolumeAbsorption")
    scatter = nodes.new("ShaderNodeVolumeScatter")
    add = nodes.new("ShaderNodeAddShader")

    absorption.inputs["Color"].default_value = (0.055, 0.48, 0.60, 1.0)
    absorption.inputs["Density"].default_value = 0.050
    scatter.inputs["Color"].default_value = (0.17, 0.54, 0.59, 1.0)
    scatter.inputs["Density"].default_value = 0.006
    scatter.inputs["Anisotropy"].default_value = 0.20

    links.new(absorption.outputs["Volume"], add.inputs[0])
    links.new(scatter.outputs["Volume"], add.inputs[1])
    links.new(add.outputs["Shader"], out.inputs["Volume"])
    return mat


def create_water_volume() -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=(0.0, 325.0, -4.0))
    volume = bpy.context.object
    volume.name = "LagoonWaterOpticalVolume"
    volume.dimensions = (700.0, 650.0, 8.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    volume.data.materials.append(make_water_volume_material())
    return volume


def create_foam() -> int:
    rng = random.Random(23)
    verts = []
    faces = []

    for band, offset in enumerate((0.7, 3.1, 6.6, 11.0)):
        x = -150.0 + rng.uniform(0.0, 4.0)
        while x < 150.0:
            length = rng.uniform(2.2, 8.5) * (1.0 - band * 0.10)
            if rng.random() < 0.82 - band * 0.08:
                x0 = x
                x1 = min(150.0, x + length)
                mid = (x0 + x1) * 0.5
                base_y = shoreline_y(mid) + offset
                base_y += 0.75 * math.sin(mid * 0.115 + band * 1.7)
                width = rng.uniform(0.10, 0.55) * (1.0 - band * 0.12)
                z = 0.085 + band * 0.005
                i = len(verts)
                verts.extend([
                    (x0, base_y - width, z),
                    (x1, base_y - width * 0.7, z),
                    (x1, base_y + width * 0.7, z),
                    (x0, base_y + width, z),
                ])
                faces.append((i, i + 1, i + 2, i + 3))
            x += length + rng.uniform(0.8, 4.5)

    mesh = bpy.data.meshes.new("FoamPatchMesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    foam = bpy.data.objects.new("ShorelineFoam", mesh)
    bpy.context.collection.objects.link(foam)

    mat = bpy.data.materials.new("Aerated white foam")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    set_input(bsdf, "Base Color", (0.96, 0.985, 0.98, 1.0))
    set_input(bsdf, "Roughness", 0.44)
    set_input(bsdf, "Transmission Weight", 0.06)
    foam.data.materials.append(mat)
    return len(faces)


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

    bg.inputs["Strength"].default_value = 0.38
    links.new(sky.outputs["Color"], bg.inputs["Color"])
    links.new(bg.outputs["Background"], out.inputs["Surface"])

    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, 40.0))
    sun = bpy.context.object
    sun.name = "TropicalNoonSun"
    sun.data.energy = 3.2
    sun.data.angle = math.radians(0.75)
    sun.rotation_euler = (math.radians(28.0), math.radians(-12.0), math.radians(-38.0))
    return sky_model


def setup_camera(scene: bpy.types.Scene) -> bpy.types.Object:
    bpy.ops.object.camera_add(location=(22.0, -55.0, 8.6))
    camera = bpy.context.object
    camera.name = "ResortCoastCamera"
    camera.data.lens = 39.0
    camera.data.sensor_width = 36.0
    camera.data.clip_start = 0.1
    camera.data.clip_end = 2500.0
    point_camera(camera, (-12.0, 105.0, -0.35))
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
    scene.view_settings.exposure = 0.15


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
            "volume": "separate closed absorption + scattering volume below surface",
        },
        "shore": {
            "wet_sand_material": True,
            "foam_patch_count": foam_count,
            "reef_patch_count": reef_count,
        },
        "objects": {
            "beach": beach.name,
            "ocean": ocean.name,
            "water_volume": volume.name,
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
