from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

import bpy
from mathutils import Vector

OUT = Path("output52")
FRAMES = OUT / "frames"
EXPERIMENT = "backrooms-note-repro"

FRAME_START = 1
FRAME_END = 24
FPS = 24
RES_X = 640
RES_Y = 360
SAMPLES = 24
ROOM_LENGTH = 65.0
ROOM_WIDTH = 15.0
CEILING_Z = 3.10
WALL_HEIGHT = 3.0
WALL_THICKNESS = 0.18
WALL_BEVEL = 0.045
AREA_POWER = 80.0
EMISSION_STRENGTH = 1.0


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
    sock = node.inputs.get(name)
    if sock is not None:
        sock.default_value = value


def make_wall_material():
    mat = bpy.data.materials.new("Procedural yellow wallpaper")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    tex = nodes.new("ShaderNodeTexNoise")
    ramp = nodes.new("ShaderNodeValToRGB")
    bump = nodes.new("ShaderNodeBump")

    tex.inputs["Scale"].default_value = 7.5
    tex.inputs["Detail"].default_value = 3.0
    tex.inputs["Roughness"].default_value = 0.7
    ramp.color_ramp.elements[0].position = 0.27
    ramp.color_ramp.elements[0].color = (0.24, 0.20, 0.075, 1.0)
    ramp.color_ramp.elements[1].position = 0.73
    ramp.color_ramp.elements[1].color = (0.58, 0.49, 0.20, 1.0)
    set_input(bsdf, "Roughness", 0.72)
    bump.inputs["Strength"].default_value = 0.16
    bump.inputs["Distance"].default_value = 0.045

    links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(tex.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def make_floor_material():
    mat = bpy.data.materials.new("Noisy old carpet")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    tex = nodes.new("ShaderNodeTexNoise")
    ramp = nodes.new("ShaderNodeValToRGB")
    bump = nodes.new("ShaderNodeBump")

    tex.inputs["Scale"].default_value = 38.0
    tex.inputs["Detail"].default_value = 4.5
    tex.inputs["Roughness"].default_value = 0.78
    ramp.color_ramp.elements[0].color = (0.11, 0.095, 0.045, 1.0)
    ramp.color_ramp.elements[1].color = (0.36, 0.30, 0.12, 1.0)
    set_input(bsdf, "Roughness", 0.92)
    bump.inputs["Strength"].default_value = 0.38
    bump.inputs["Distance"].default_value = 0.065

    links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(tex.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def make_simple_material(name: str, color, roughness: float):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    set_input(bsdf, "Base Color", color)
    set_input(bsdf, "Roughness", roughness)
    return mat


def make_emission_material():
    mat = bpy.data.materials.new("Fluorescent panel glow")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = (0.86, 0.90, 0.66, 1.0)
    emission.inputs["Strength"].default_value = EMISSION_STRENGTH
    links.new(emission.outputs["Emission"], out.inputs["Surface"])
    return mat


def add_box(name: str, center, size, material, bevel: float = 0.0):
    bpy.ops.mesh.primitive_cube_add(location=center)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (size[0] / 2.0, size[1] / 2.0, size[2] / 2.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material is not None:
        obj.data.materials.append(material)
    if bevel > 0:
        mod = obj.modifiers.new(name="Soft wall corners", type="BEVEL")
        mod.width = bevel
        mod.segments = 2
    return obj


def add_wall(name: str, cx: float, cy: float, sx: float, sy: float, material):
    return add_box(
        name,
        (cx, cy, WALL_HEIGHT / 2.0),
        (sx, sy, WALL_HEIGHT),
        material,
        WALL_BEVEL,
    )


def point_camera(camera: bpy.types.Object, target) -> None:
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def setup_color_grade(scene: bpy.types.Scene) -> bool:
    try:
        scene.use_nodes = True
        nodes = scene.node_tree.nodes
        links = scene.node_tree.links
        nodes.clear()
        render_layers = nodes.new("CompositorNodeRLayers")
        hue_sat = nodes.new("CompositorNodeHueSat")
        bright_contrast = nodes.new("CompositorNodeBrightContrast")
        composite = nodes.new("CompositorNodeComposite")
        hue_sat.inputs["Saturation"].default_value = 0.68
        hue_sat.inputs["Value"].default_value = 0.92
        bright_contrast.inputs["Bright"].default_value = -1.5
        bright_contrast.inputs["Contrast"].default_value = -4.0
        links.new(render_layers.outputs["Image"], hue_sat.inputs["Image"])
        links.new(hue_sat.outputs["Image"], bright_contrast.inputs["Image"])
        links.new(bright_contrast.outputs["Image"], composite.inputs["Image"])
        return True
    except Exception as exc:
        print(f"COLOR_GRADE_FALLBACK={exc!r}")
        return False


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
    scene.render.image_settings.color_mode = "RGB"
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = True

    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Medium Low Contrast"
    except Exception as exc:
        print(f"COLOR_MANAGEMENT_FALLBACK={exc!r}")
    scene.view_settings.exposure = -0.15

    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.025, 0.027, 0.018, 1.0)
    bg.inputs["Strength"].default_value = 0.035

    wall_mat = make_wall_material()
    floor_mat = make_floor_material()
    ceiling_mat = make_simple_material("Ceiling", (0.48, 0.47, 0.32, 1.0), 0.9)
    skirting_mat = make_simple_material("Skirting", (0.10, 0.085, 0.035, 1.0), 0.72)
    emit_mat = make_emission_material()

    add_box("Floor", (0.0, 0.0, -0.075), (ROOM_LENGTH, ROOM_WIDTH, 0.15), floor_mat)
    add_box("Ceiling", (0.0, 0.0, CEILING_Z + 0.06), (ROOM_LENGTH, ROOM_WIDTH, 0.12), ceiling_mat)

    wall_specs = [
        (0.0, -7.42, 65.0, WALL_THICKNESS),
        (0.0, 7.42, 65.0, WALL_THICKNESS),
        (-32.42, 0.0, WALL_THICKNESS, 15.0),
        (32.42, 0.0, WALL_THICKNESS, 15.0),
        (-24.0, -2.8, 12.0, WALL_THICKNESS),
        (-10.0, -2.8, 8.0, WALL_THICKNESS),
        (4.0, -2.8, 12.0, WALL_THICKNESS),
        (20.0, -2.8, 15.0, WALL_THICKNESS),
        (-19.0, 2.9, 13.0, WALL_THICKNESS),
        (-1.5, 2.9, 13.0, WALL_THICKNESS),
        (17.0, 2.9, 12.0, WALL_THICKNESS),
        (-26.0, -5.1, WALL_THICKNESS, 4.6),
        (-20.0, 0.1, WALL_THICKNESS, 5.6),
        (-14.0, 5.0, WALL_THICKNESS, 4.8),
        (-7.0, -5.1, WALL_THICKNESS, 4.6),
        (-3.0, 0.1, WALL_THICKNESS, 5.6),
        (5.0, 5.0, WALL_THICKNESS, 4.8),
        (10.5, -5.1, WALL_THICKNESS, 4.6),
        (14.0, 0.1, WALL_THICKNESS, 5.6),
        (23.0, 5.0, WALL_THICKNESS, 4.8),
        (27.0, -5.1, WALL_THICKNESS, 4.6),
        (-28.5, 4.8, 5.5, WALL_THICKNESS),
        (-12.0, -5.3, 4.0, WALL_THICKNESS),
        (8.0, 5.2, 5.5, WALL_THICKNESS),
        (25.0, 0.3, 5.0, WALL_THICKNESS),
    ]

    walls = []
    for idx, (cx, cy, sx, sy) in enumerate(wall_specs, 1):
        wall = add_wall(f"Wall_{idx:02d}", cx, cy, sx, sy, wall_mat)
        walls.append(wall)
        add_box(
            f"Skirting_{idx:02d}",
            (cx, cy, 0.055),
            (sx + (0.02 if sx > sy else 0.0), sy + (0.02 if sy > sx else 0.0), 0.11),
            skirting_mat,
            0.012,
        )

    panel_positions = []
    for x in (-27.0, -18.0, -9.0, 0.0, 9.0, 18.0, 27.0):
        for y in (-4.6, 0.0, 4.6):
            panel_positions.append((x, y))

    area_lights = []
    for idx, (x, y) in enumerate(panel_positions, 1):
        bpy.ops.mesh.primitive_plane_add(size=2.0, location=(x, y, CEILING_Z - 0.075))
        panel = bpy.context.object
        panel.name = f"FluorescentPanel_{idx:02d}"
        panel.scale = (0.72, 0.16, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        panel.data.materials.append(emit_mat)

        bpy.ops.object.light_add(type="AREA", location=(x, y, CEILING_Z - 0.11))
        light = bpy.context.object
        light.name = f"AreaLight_{idx:02d}"
        light.data.energy = AREA_POWER
        light.data.shape = "RECTANGLE"
        light.data.size = 1.55
        light.data.size_y = 0.45
        light.data.color = (0.94, 0.97, 0.72)
        light["base_energy"] = AREA_POWER
        area_lights.append(light)

    bpy.ops.object.light_add(type="AREA", location=(-28.0, -5.0, 2.75))
    front_fill = bpy.context.object
    front_fill.name = "FrontFill_Area80"
    front_fill.data.energy = AREA_POWER
    front_fill.data.shape = "DISK"
    front_fill.data.size = 2.5
    point_camera(front_fill, (-21.0, -3.0, 1.0))
    area_lights.append(front_fill)

    bpy.ops.object.camera_add(location=(-28.6, -5.2, 1.58))
    camera = bpy.context.object
    camera.name = "Camera_30mm"
    camera.data.lens = 30.0
    camera.data.sensor_width = 36.0
    point_camera(camera, (-2.0, -1.1, 1.46))
    scene.camera = camera

    compositor_grade = setup_color_grade(scene)
    return scene, camera, area_lights, walls, compositor_grade


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)
    scene, camera, area_lights, walls, compositor_grade = setup_scene()
    base_camera = camera.location.copy()

    frame_stats = []
    for frame in range(FRAME_START, FRAME_END + 1):
        t = (frame - FRAME_START) / max(1, FRAME_END - FRAME_START)
        camera.location = (
            base_camera.x + 0.72 * t,
            base_camera.y + 0.08 * math.sin(t * math.tau),
            base_camera.z + 0.015 * math.sin(t * math.tau * 0.5),
        )
        point_camera(
            camera,
            (-2.0 + 0.5 * t, -1.1 + 0.06 * math.sin(t * math.tau), 1.46),
        )

        for idx, light in enumerate(area_lights):
            phase = idx * 0.47
            flicker = 0.97 + 0.03 * math.sin(t * math.tau * 2.0 + phase)
            if idx == 5:
                flicker *= 0.86 + 0.14 * abs(math.sin(t * math.tau * 3.0))
            light.data.energy = AREA_POWER * flicker

        scene.frame_set(frame)
        bpy.context.view_layer.update()
        scene.render.filepath = str(FRAMES / f"frame_{frame:04d}.png")
        bpy.ops.render.render(write_still=True)
        frame_stats.append({
            "frame": frame,
            "camera": [round(float(v), 5) for v in camera.location],
            "flicker_light_w": round(float(area_lights[5].data.energy), 4),
        })

    preview_frame = 12
    shutil.copy2(FRAMES / f"frame_{preview_frame:04d}.png", OUT / "preview.png")

    report = {
        "experiment": EXPERIMENT,
        "source_article": "https://note.com/kitaniosam/n/ne760c5e78985",
        "blender_version": bpy.app.version_string,
        "engine": scene.render.engine,
        "device": "CPU",
        "samples": SAMPLES,
        "frame_start": FRAME_START,
        "frame_end": FRAME_END,
        "frame_count": FRAME_END - FRAME_START + 1,
        "fps": FPS,
        "resolution": [RES_X, RES_Y],
        "preview_frame": preview_frame,
        "room_size_m": [ROOM_LENGTH, ROOM_WIDTH],
        "camera_lens_mm": float(camera.data.lens),
        "wall_bevel_m": WALL_BEVEL,
        "wall_count": len(walls),
        "emission_strength": EMISSION_STRENGTH,
        "emission_panel_count": 21,
        "area_light_power_w": AREA_POWER,
        "area_light_count": len(area_lights),
        "procedural_materials_only": True,
        "external_texture_files": 0,
        "compositor_grade": compositor_grade,
        "grade_intent": "reduced saturation and slightly softened contrast",
        "frame_stats": frame_stats,
    }
    (OUT / f"{EXPERIMENT}-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f"{EXPERIMENT}.blend"))

    print(f"BLENDER52_VERSION={bpy.app.version_string}")
    print(f"BLENDER52_ENGINE={scene.render.engine}")
    print(f"BLENDER52_FRAMES={report['frame_count']}")
    print(f"BACKROOMS_WALLS={report['wall_count']}")
    print(f"BACKROOMS_LIGHTS={report['area_light_count']}")


if __name__ == "__main__":
    main()
