from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

import bpy
from mathutils import Vector

OUT = Path("output52")
FRAMES = OUT / "frames"
FRAME_END = 36
FPS = 24
RES_X = 480
RES_Y = 360


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def choose_engine(scene):
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = engine
            return engine
        except Exception:
            pass
    raise RuntimeError("No EEVEE render engine available")


def configure_scene(transparent=False):
    clear_scene()
    OUT.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = FRAME_END
    scene.render.fps = FPS
    scene.render.resolution_x = RES_X
    scene.render.resolution_y = RES_Y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = transparent
    choose_engine(scene)
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.012, 0.018, 0.035, 1.0)
    bg.inputs["Strength"].default_value = 0.22
    return scene


def material(name, color, metallic=0.0, roughness=0.35):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def point_at(obj, target=(0.0, 0.0, 1.0)):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_stage(scene, target=(0, 0, 1.4)):
    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, 0))
    floor = bpy.context.object
    floor.data.materials.append(material("Floor", (0.045, 0.06, 0.09, 1), 0.08, 0.5))

    bpy.ops.object.light_add(type="AREA", location=(-3.5, -3.0, 6.5))
    key = bpy.context.object
    key.data.energy = 1050
    key.data.size = 4.0
    point_at(key, target)

    bpy.ops.object.light_add(type="AREA", location=(4.0, -1.0, 3.5))
    fill = bpy.context.object
    fill.data.energy = 650
    fill.data.size = 3.0
    point_at(fill, target)

    bpy.ops.object.camera_add(location=(6.5, -7.5, 4.8))
    cam = bpy.context.object
    cam.data.lens = 50
    point_at(cam, target)
    scene.camera = cam


def render_sequence(scene, experiment, report, per_frame=None, preview_frame=18):
    samples = []
    for frame in range(1, FRAME_END + 1):
        scene.frame_set(frame)
        if per_frame:
            sample = per_frame(frame)
            if sample is not None:
                samples.append(sample)
        bpy.context.view_layer.update()
        scene.render.filepath = str(FRAMES / f"frame_{frame:04d}.png")
        bpy.ops.render.render(write_still=True)

    shutil.copy2(FRAMES / f"frame_{preview_frame:04d}.png", OUT / "preview.png")
    report.update({
        "experiment": experiment,
        "blender_version": bpy.app.version_string,
        "engine": scene.render.engine,
        "frame_count": FRAME_END,
        "fps": FPS,
        "resolution": [RES_X, RES_Y],
        "preview_frame": preview_frame,
        "samples": samples,
    })
    (OUT / f"{experiment}-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f"{experiment}.blend"))
    print(f"BLENDER52_VERSION={bpy.app.version_string}")
    print(f"FEATURE52_EXPERIMENT={experiment}")


def thin_wall():
    experiment = "feature52-thin-wall"
    scene = configure_scene()
    add_stage(scene, (0, 0, 1.8))
    mat = material("ThinWallGlass", (0.22, 0.65, 1.0, 1.0), 0.0, 0.12)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    missing = [name for name in ("Transmission Weight", "Thin Wall") if bsdf.inputs.get(name) is None]
    if missing:
        raise RuntimeError(f"Blender 5.2 Principled inputs missing: {missing}")
    bsdf.inputs["Transmission Weight"].default_value = 0.92
    bsdf.inputs["IOR"].default_value = 1.45
    bsdf.inputs["Thin Wall"].default_value = True

    panels = []
    for i, x in enumerate((-1.7, 0.0, 1.7)):
        bpy.ops.mesh.primitive_plane_add(
            size=2.7, location=(x, 0.25 * i, 1.75), rotation=(math.radians(90), 0, 0)
        )
        panel = bpy.context.object
        panel.data.materials.append(mat)
        panels.append(panel)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.42, location=(x, 1.0, 1.7))
        orb = bpy.context.object
        orb.data.materials.append(
            material(f"Orb{i}", (0.95, 0.12 + 0.3*i, 0.08 + 0.3*(2-i), 1), 0.15, 0.22)
        )

    def per_frame(frame):
        phase = (frame - 1) / (FRAME_END - 1)
        for i, panel in enumerate(panels):
            panel.rotation_euler.z = math.radians(-28 + 56 * phase + i * 8)
        return {"frame": frame, "rotation_z": float(panels[1].rotation_euler.z)}

    render_sequence(scene, experiment, {
        "feature": {
            "name": "Principled BSDF Thin Wall",
            "node_idname": bsdf.bl_idname,
            "thin_wall_input_present": "Thin Wall" in bsdf.inputs,
            "thin_wall_enabled": bool(bsdf.inputs["Thin Wall"].default_value),
            "transmission_weight": float(bsdf.inputs["Transmission Weight"].default_value),
        }
    }, per_frame)


def shader_scene_time():
    experiment = "feature52-shader-scene-time"
    scene = configure_scene()
    add_stage(scene)
    mat = bpy.data.materials.new("SceneTimePulse")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    scene_time = nodes.new("GeometryNodeInputSceneTime")
    multiply = nodes.new("ShaderNodeMath")
    multiply.operation = "MULTIPLY"
    multiply.inputs[1].default_value = 0.42
    sine = nodes.new("ShaderNodeMath")
    sine.operation = "SINE"
    scale = nodes.new("ShaderNodeMath")
    scale.operation = "MULTIPLY"
    scale.inputs[1].default_value = 3.5
    bias = nodes.new("ShaderNodeMath")
    bias.operation = "ADD"
    bias.inputs[1].default_value = 4.0
    emission.inputs["Color"].default_value = (0.08, 0.55, 1.0, 1.0)
    links = mat.node_tree.links
    links.new(scene_time.outputs["Frame"], multiply.inputs[0])
    links.new(multiply.outputs[0], sine.inputs[0])
    links.new(sine.outputs[0], scale.inputs[0])
    links.new(scale.outputs[0], bias.inputs[0])
    links.new(bias.outputs[0], emission.inputs["Strength"])
    links.new(emission.outputs[0], out.inputs["Surface"])

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=1.45, location=(0, 0, 1.55))
    hero = bpy.context.object
    hero.data.materials.append(mat)
    bpy.ops.mesh.primitive_torus_add(major_radius=2.25, minor_radius=0.10, location=(0, 0, 1.55))
    bpy.context.object.data.materials.append(mat)

    render_sequence(scene, experiment, {
        "feature": {
            "name": "Shader Scene Time Node",
            "node_idname": scene_time.bl_idname,
            "outputs": [s.name for s in scene_time.outputs],
        }
    }, preview_frame=11)


def compositor_blank_image():
    experiment = "feature52-compositor-blank-image"
    scene = configure_scene(transparent=True)

    bpy.ops.mesh.primitive_monkey_add(location=(0, 0, 1.45))
    hero = bpy.context.object
    hero.data.materials.append(material("Hero", (0.95, 0.34, 0.08, 1), 0.35, 0.28))
    bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_torus_add(major_radius=2.0, minor_radius=0.12, location=(0, 0, 1.45))
    bpy.context.object.data.materials.append(material("Ring", (0.1, 0.65, 1.0, 1), 0.55, 0.25))

    bpy.ops.object.light_add(type="AREA", location=(-3.5, -3, 6))
    bpy.context.object.data.energy = 1100
    bpy.context.object.data.size = 4
    point_at(bpy.context.object, (0, 0, 1.3))
    bpy.ops.object.camera_add(location=(6.0, -7.6, 4.0))
    cam = bpy.context.object
    cam.data.lens = 50
    point_at(cam, (0, 0, 1.4))
    scene.camera = cam

    scene.use_nodes = True
    nodes = scene.node_tree.nodes
    nodes.clear()
    render = nodes.new("CompositorNodeRLayers")
    blank = nodes.new("CompositorNodeBlankImage")
    over = nodes.new("CompositorNodeAlphaOver")
    comp = nodes.new("CompositorNodeComposite")
    blank.inputs["Color"].default_value = (0.015, 0.09, 0.19, 1.0)
    if blank.inputs.get("Size") is not None:
        blank.inputs["Size"].default_value = (480, 360)
    scene.node_tree.links.new(blank.outputs["Image"], over.inputs[1])
    scene.node_tree.links.new(render.outputs["Image"], over.inputs[2])
    scene.node_tree.links.new(over.outputs["Image"], comp.inputs["Image"])

    def per_frame(frame):
        hero.rotation_euler.z = (frame - 1) / (FRAME_END - 1) * math.tau
        return {"frame": frame, "rotation_z": float(hero.rotation_euler.z)}

    render_sequence(scene, experiment, {
        "feature": {
            "name": "Compositor Blank Image",
            "node_idname": blank.bl_idname,
            "inputs": [s.name for s in blank.inputs],
            "size_socket_present": blank.inputs.get("Size") is not None,
        }
    }, per_frame)


def compositor_string_to_image():
    experiment = "feature52-compositor-string-to-image"
    scene = configure_scene()
    bpy.ops.mesh.primitive_cube_add(size=2.4, location=(0, 0, 1.45), rotation=(0.25, 0.25, 0))
    hero = bpy.context.object
    hero.data.materials.append(material("Hero", (0.11, 0.34, 0.95, 1), 0.5, 0.2))
    bpy.ops.object.light_add(type="AREA", location=(-3.5, -3, 6))
    bpy.context.object.data.energy = 1200
    bpy.context.object.data.size = 4
    point_at(bpy.context.object, (0, 0, 1.3))
    bpy.ops.object.camera_add(location=(6.0, -7.2, 4.4))
    cam = bpy.context.object
    cam.data.lens = 50
    point_at(cam, (0, 0, 1.4))
    scene.camera = cam

    scene.use_nodes = True
    nodes = scene.node_tree.nodes
    nodes.clear()
    render = nodes.new("CompositorNodeRLayers")
    text = nodes.new("CompositorNodeStringToImage")
    over = nodes.new("CompositorNodeAlphaOver")
    comp = nodes.new("CompositorNodeComposite")
    text.inputs["String"].default_value = "BLENDER 5.2"
    text.inputs["Size"].default_value = 64.0
    scene.node_tree.links.new(render.outputs["Image"], over.inputs[1])
    scene.node_tree.links.new(text.outputs["Image"], over.inputs[2])
    scene.node_tree.links.new(over.outputs["Image"], comp.inputs["Image"])

    def per_frame(frame):
        hero.rotation_euler.z = (frame - 1) / (FRAME_END - 1) * math.tau
        hero.rotation_euler.x = 0.25 + 0.12 * math.sin((frame - 1) / (FRAME_END - 1) * math.tau)
        return {"frame": frame, "rotation_z": float(hero.rotation_euler.z)}

    render_sequence(scene, experiment, {
        "feature": {
            "name": "Compositor String to Image",
            "node_idname": text.bl_idname,
            "string": text.inputs["String"].default_value,
            "size": float(text.inputs["Size"].default_value),
            "outputs": [s.name for s in text.outputs],
        }
    }, per_frame)


def run(experiment):
    table = {
        "feature52-thin-wall": thin_wall,
        "feature52-shader-scene-time": shader_scene_time,
        "feature52-compositor-blank-image": compositor_blank_image,
        "feature52-compositor-string-to-image": compositor_string_to_image,
    }
    try:
        fn = table[experiment]
    except KeyError:
        raise SystemExit(f"unknown showcase experiment: {experiment}")
    fn()
