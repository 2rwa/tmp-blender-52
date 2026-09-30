from __future__ import annotations

import json
import math
import os
import shutil
from pathlib import Path

import bpy
from mathutils import Vector

FAST_PREVIEW = os.environ.get("BACKROOMS_FAST_PREVIEW", "0") == "1"
VARIANT_SWEEP = os.environ.get("BACKROOMS_VARIANT_SWEEP", "0") == "1"
VARIANT_ID = int(os.environ.get("BACKROOMS_VARIANT", "0"))
OUT = Path(os.environ.get("BACKROOMS_OUTPUT", "output52"))
FRAMES = OUT / "frames"
EXPERIMENT = "backrooms-note-repro"

FRAME_START = 1
FRAME_END = 1 if VARIANT_SWEEP else (3 if FAST_PREVIEW else 24)
FPS = 24
RES_X = 320 if (FAST_PREVIEW or VARIANT_SWEEP) else 640
RES_Y = 180 if (FAST_PREVIEW or VARIANT_SWEEP) else 360
SAMPLES = 8 if (FAST_PREVIEW or VARIANT_SWEEP) else 24
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


def variant_config() -> dict:
    variants = {
        1: {
            "name": "clean-yellow",
            "wall_dark": (0.30, 0.255, 0.070, 1.0),
            "wall_light": (0.74, 0.65, 0.22, 1.0),
            "floor_dark": (0.10, 0.085, 0.035, 1.0),
            "floor_light": (0.30, 0.255, 0.10, 1.0),
            "light_color": (0.97, 1.00, 0.78),
            "light_power": 95.0,
            "exposure": -0.05,
            "camera": (-19.5, 1.0, 1.58),
            "target": (-7.9, -2.1, 1.46),
        },
        2: {
            "name": "sickly-green",
            "wall_dark": (0.25, 0.255, 0.065, 1.0),
            "wall_light": (0.62, 0.65, 0.19, 1.0),
            "floor_dark": (0.075, 0.080, 0.035, 1.0),
            "floor_light": (0.24, 0.245, 0.09, 1.0),
            "light_color": (0.86, 1.00, 0.70),
            "light_power": 100.0,
            "exposure": -0.10,
            "camera": (-19.5, 1.0, 1.58),
            "target": (-7.9, -2.1, 1.46),
        },
        3: {
            "name": "deep-mustard",
            "wall_dark": (0.34, 0.25, 0.055, 1.0),
            "wall_light": (0.78, 0.56, 0.14, 1.0),
            "floor_dark": (0.11, 0.075, 0.028, 1.0),
            "floor_light": (0.32, 0.22, 0.075, 1.0),
            "light_color": (1.00, 0.93, 0.68),
            "light_power": 90.0,
            "exposure": -0.12,
            "camera": (-19.5, 1.0, 1.58),
            "target": (-7.9, -2.1, 1.46),
        },
        4: {
            "name": "fluorescent-boost",
            "wall_dark": (0.29, 0.245, 0.070, 1.0),
            "wall_light": (0.70, 0.61, 0.20, 1.0),
            "floor_dark": (0.10, 0.085, 0.035, 1.0),
            "floor_light": (0.30, 0.255, 0.10, 1.0),
            "light_color": (0.94, 1.00, 0.76),
            "light_power": 135.0,
            "exposure": -0.20,
            "camera": (-19.5, 1.0, 1.58),
            "target": (-7.9, -2.1, 1.46),
        },
        5: {
            "name": "warm-fluorescent",
            "wall_dark": (0.31, 0.245, 0.060, 1.0),
            "wall_light": (0.73, 0.59, 0.18, 1.0),
            "floor_dark": (0.105, 0.078, 0.032, 1.0),
            "floor_light": (0.31, 0.235, 0.085, 1.0),
            "light_color": (1.00, 0.88, 0.60),
            "light_power": 110.0,
            "exposure": -0.10,
            "camera": (-19.5, 1.0, 1.58),
            "target": (-7.9, -2.1, 1.46),
        },
        6: {
            "name": "dim-liminal",
            "wall_dark": (0.26, 0.22, 0.060, 1.0),
            "wall_light": (0.62, 0.52, 0.16, 1.0),
            "floor_dark": (0.075, 0.063, 0.026, 1.0),
            "floor_light": (0.24, 0.20, 0.070, 1.0),
            "light_color": (0.91, 0.95, 0.70),
            "light_power": 72.0,
            "exposure": -0.45,
            "camera": (-19.5, 1.0, 1.58),
            "target": (-7.9, -2.1, 1.46),
        },
        7: {
            "name": "bright-liminal",
            "wall_dark": (0.33, 0.29, 0.085, 1.0),
            "wall_light": (0.82, 0.75, 0.28, 1.0),
            "floor_dark": (0.12, 0.105, 0.045, 1.0),
            "floor_light": (0.36, 0.32, 0.13, 1.0),
            "light_color": (1.00, 1.00, 0.82),
            "light_power": 145.0,
            "exposure": 0.05,
            "camera": (-19.5, 1.0, 1.58),
            "target": (-7.9, -2.1, 1.46),
        },
        8: {
            "name": "left-wall-composition",
            "wall_dark": (0.30, 0.255, 0.070, 1.0),
            "wall_light": (0.74, 0.65, 0.22, 1.0),
            "floor_dark": (0.10, 0.085, 0.035, 1.0),
            "floor_light": (0.30, 0.255, 0.10, 1.0),
            "light_color": (0.97, 1.00, 0.78),
            "light_power": 105.0,
            "exposure": -0.08,
            "camera": (-19.8, 1.65, 1.58),
            "target": (-8.2, -1.65, 1.43),
        },
        9: {
            "name": "lower-eye-composition",
            "wall_dark": (0.30, 0.255, 0.070, 1.0),
            "wall_light": (0.74, 0.65, 0.22, 1.0),
            "floor_dark": (0.10, 0.085, 0.035, 1.0),
            "floor_light": (0.30, 0.255, 0.10, 1.0),
            "light_color": (0.97, 1.00, 0.78),
            "light_power": 110.0,
            "exposure": -0.08,
            "camera": (-19.5, 0.8, 1.35),
            "target": (-7.7, -2.15, 1.40),
        },
        10: {
            "name": "ceiling-emphasis",
            "wall_dark": (0.30, 0.255, 0.070, 1.0),
            "wall_light": (0.74, 0.65, 0.22, 1.0),
            "floor_dark": (0.10, 0.085, 0.035, 1.0),
            "floor_light": (0.30, 0.255, 0.10, 1.0),
            "light_color": (0.97, 1.00, 0.78),
            "light_power": 120.0,
            "exposure": -0.10,
            "camera": (-19.5, 1.0, 1.48),
            "target": (-7.9, -2.1, 1.72),
        },
        11: {
            "name": "v8-warm-balanced",
            "wall_dark": (0.31, 0.245, 0.060, 1.0),
            "wall_light": (0.73, 0.59, 0.18, 1.0),
            "floor_dark": (0.105, 0.078, 0.032, 1.0),
            "floor_light": (0.31, 0.235, 0.085, 1.0),
            "light_color": (0.94, 1.00, 0.76),
            "light_power": 125.0,
            "exposure": -0.12,
            "camera": (-19.8, 1.65, 1.58),
            "target": (-8.2, -1.65, 1.43),
            "wall_scale": 5.8,
            "wall_detail": 2.2,
            "wall_bump": 0.10,
            "floor_scale": 48.0,
            "floor_bump": 0.48,
            "panel_scale": (0.82, 0.19),
            "area_size": (1.75, 0.52),
            "emission_strength": 1.15,
        },
        12: {
            "name": "v8-sickly-green",
            "wall_dark": (0.285, 0.255, 0.058, 1.0),
            "wall_light": (0.68, 0.64, 0.18, 1.0),
            "floor_dark": (0.095, 0.083, 0.032, 1.0),
            "floor_light": (0.28, 0.245, 0.082, 1.0),
            "light_color": (0.90, 1.00, 0.74),
            "light_power": 130.0,
            "exposure": -0.14,
            "camera": (-19.8, 1.65, 1.58),
            "target": (-8.2, -1.65, 1.43),
            "wall_scale": 5.8,
            "wall_detail": 2.2,
            "wall_bump": 0.10,
            "floor_scale": 48.0,
            "floor_bump": 0.48,
            "panel_scale": (0.82, 0.19),
            "area_size": (1.75, 0.52),
            "emission_strength": 1.15,
        },
        13: {
            "name": "v8-deep-mustard",
            "wall_dark": (0.335, 0.245, 0.052, 1.0),
            "wall_light": (0.77, 0.57, 0.15, 1.0),
            "floor_dark": (0.11, 0.075, 0.030, 1.0),
            "floor_light": (0.33, 0.225, 0.075, 1.0),
            "light_color": (0.98, 0.96, 0.70),
            "light_power": 122.0,
            "exposure": -0.14,
            "camera": (-19.8, 1.65, 1.58),
            "target": (-8.2, -1.65, 1.43),
            "wall_scale": 5.8,
            "wall_detail": 2.2,
            "wall_bump": 0.11,
            "floor_scale": 48.0,
            "floor_bump": 0.48,
            "panel_scale": (0.82, 0.19),
            "area_size": (1.75, 0.52),
            "emission_strength": 1.15,
        },
        14: {
            "name": "v8-big-fluorescents",
            "wall_dark": (0.31, 0.245, 0.060, 1.0),
            "wall_light": (0.73, 0.59, 0.18, 1.0),
            "floor_dark": (0.105, 0.078, 0.032, 1.0),
            "floor_light": (0.31, 0.235, 0.085, 1.0),
            "light_color": (0.94, 1.00, 0.76),
            "light_power": 138.0,
            "exposure": -0.18,
            "camera": (-19.8, 1.65, 1.58),
            "target": (-8.2, -1.65, 1.43),
            "wall_scale": 5.8,
            "wall_detail": 2.2,
            "wall_bump": 0.10,
            "floor_scale": 48.0,
            "floor_bump": 0.48,
            "panel_scale": (0.96, 0.22),
            "area_size": (2.05, 0.60),
            "emission_strength": 1.40,
        },
        15: {
            "name": "v8-ceiling-heavy",
            "wall_dark": (0.31, 0.245, 0.060, 1.0),
            "wall_light": (0.73, 0.59, 0.18, 1.0),
            "floor_dark": (0.105, 0.078, 0.032, 1.0),
            "floor_light": (0.31, 0.235, 0.085, 1.0),
            "light_color": (0.94, 1.00, 0.76),
            "light_power": 130.0,
            "exposure": -0.13,
            "camera": (-19.8, 1.65, 1.46),
            "target": (-8.2, -1.65, 1.72),
            "wall_scale": 5.8,
            "wall_detail": 2.2,
            "wall_bump": 0.10,
            "floor_scale": 48.0,
            "floor_bump": 0.48,
            "panel_scale": (0.90, 0.21),
            "area_size": (1.90, 0.56),
            "emission_strength": 1.30,
        },
        16: {
            "name": "coarse-wallpaper",
            "wall_dark": (0.31, 0.245, 0.060, 1.0),
            "wall_light": (0.73, 0.59, 0.18, 1.0),
            "floor_dark": (0.105, 0.078, 0.032, 1.0),
            "floor_light": (0.31, 0.235, 0.085, 1.0),
            "light_color": (0.94, 1.00, 0.76),
            "light_power": 125.0,
            "exposure": -0.12,
            "camera": (-19.8, 1.65, 1.58),
            "target": (-8.2, -1.65, 1.43),
            "wall_scale": 3.9,
            "wall_detail": 1.6,
            "wall_bump": 0.075,
            "floor_scale": 48.0,
            "floor_bump": 0.48,
            "panel_scale": (0.82, 0.19),
            "area_size": (1.75, 0.52),
            "emission_strength": 1.15,
        },
        17: {
            "name": "fine-wallpaper",
            "wall_dark": (0.31, 0.245, 0.060, 1.0),
            "wall_light": (0.73, 0.59, 0.18, 1.0),
            "floor_dark": (0.105, 0.078, 0.032, 1.0),
            "floor_light": (0.31, 0.235, 0.085, 1.0),
            "light_color": (0.94, 1.00, 0.76),
            "light_power": 125.0,
            "exposure": -0.12,
            "camera": (-19.8, 1.65, 1.58),
            "target": (-8.2, -1.65, 1.43),
            "wall_scale": 10.0,
            "wall_detail": 3.2,
            "wall_bump": 0.075,
            "floor_scale": 48.0,
            "floor_bump": 0.48,
            "panel_scale": (0.82, 0.19),
            "area_size": (1.75, 0.52),
            "emission_strength": 1.15,
        },
        18: {
            "name": "strong-carpet",
            "wall_dark": (0.31, 0.245, 0.060, 1.0),
            "wall_light": (0.73, 0.59, 0.18, 1.0),
            "floor_dark": (0.095, 0.070, 0.028, 1.0),
            "floor_light": (0.34, 0.25, 0.090, 1.0),
            "light_color": (0.94, 1.00, 0.76),
            "light_power": 125.0,
            "exposure": -0.12,
            "camera": (-19.8, 1.65, 1.58),
            "target": (-8.2, -1.65, 1.43),
            "wall_scale": 5.8,
            "wall_detail": 2.2,
            "wall_bump": 0.10,
            "floor_scale": 65.0,
            "floor_bump": 0.68,
            "panel_scale": (0.82, 0.19),
            "area_size": (1.75, 0.52),
            "emission_strength": 1.15,
        },
        19: {
            "name": "overhead-glow",
            "wall_dark": (0.30, 0.25, 0.060, 1.0),
            "wall_light": (0.71, 0.61, 0.18, 1.0),
            "floor_dark": (0.105, 0.078, 0.032, 1.0),
            "floor_light": (0.31, 0.235, 0.085, 1.0),
            "light_color": (0.92, 1.00, 0.72),
            "light_power": 155.0,
            "exposure": -0.28,
            "camera": (-19.8, 1.65, 1.53),
            "target": (-8.2, -1.65, 1.62),
            "wall_scale": 5.8,
            "wall_detail": 2.2,
            "wall_bump": 0.10,
            "floor_scale": 48.0,
            "floor_bump": 0.48,
            "panel_scale": (1.00, 0.23),
            "area_size": (2.15, 0.64),
            "emission_strength": 1.55,
        },
        20: {
            "name": "yellow-green-balanced",
            "wall_dark": (0.305, 0.265, 0.058, 1.0),
            "wall_light": (0.735, 0.665, 0.19, 1.0),
            "floor_dark": (0.10, 0.082, 0.030, 1.0),
            "floor_light": (0.30, 0.25, 0.082, 1.0),
            "light_color": (0.93, 1.00, 0.73),
            "light_power": 132.0,
            "exposure": -0.15,
            "camera": (-19.8, 1.65, 1.58),
            "target": (-8.2, -1.65, 1.43),
            "wall_scale": 5.2,
            "wall_detail": 2.0,
            "wall_bump": 0.09,
            "floor_scale": 52.0,
            "floor_bump": 0.52,
            "panel_scale": (0.88, 0.20),
            "area_size": (1.88, 0.55),
            "emission_strength": 1.25,
        },
    }
    return variants.get(VARIANT_ID, {
        "name": "baseline",
        "wall_dark": (0.24, 0.20, 0.075, 1.0),
        "wall_light": (0.58, 0.49, 0.20, 1.0),
        "floor_dark": (0.11, 0.095, 0.045, 1.0),
        "floor_light": (0.36, 0.30, 0.12, 1.0),
        "light_color": (0.94, 0.97, 0.72),
        "light_power": AREA_POWER,
        "exposure": -0.15,
        "camera": (-19.5, 1.0, 1.58),
        "target": (-7.9, -2.1, 1.46),
    })


VARIANT = variant_config()

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

    tex.inputs["Scale"].default_value = VARIANT.get("wall_scale", 7.5)
    tex.inputs["Detail"].default_value = VARIANT.get("wall_detail", 3.0)
    tex.inputs["Roughness"].default_value = 0.7
    ramp.color_ramp.elements[0].position = 0.27
    ramp.color_ramp.elements[0].color = VARIANT["wall_dark"]
    ramp.color_ramp.elements[1].position = 0.73
    ramp.color_ramp.elements[1].color = VARIANT["wall_light"]
    set_input(bsdf, "Roughness", 0.72)
    bump.inputs["Strength"].default_value = VARIANT.get("wall_bump", 0.16)
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

    tex.inputs["Scale"].default_value = VARIANT.get("floor_scale", 38.0)
    tex.inputs["Detail"].default_value = 4.5
    tex.inputs["Roughness"].default_value = 0.78
    ramp.color_ramp.elements[0].color = VARIANT["floor_dark"]
    ramp.color_ramp.elements[1].color = VARIANT["floor_light"]
    set_input(bsdf, "Roughness", 0.92)
    bump.inputs["Strength"].default_value = VARIANT.get("floor_bump", 0.38)
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
    emission.inputs["Strength"].default_value = VARIANT.get("emission_strength", EMISSION_STRENGTH)
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
        scene.render.use_compositing = True

        if bpy.app.version >= (5, 0, 0):
            # Blender 5.x moved the compositor out of scene.node_tree.
            tree = bpy.data.node_groups.new(
                "Backrooms Compositor",
                "CompositorNodeTree",
            )
            scene.compositing_node_group = tree
            render_layers = tree.nodes.new("CompositorNodeRLayers")
            hue_sat = tree.nodes.new("CompositorNodeHueSat")
            bright_contrast = tree.nodes.new("CompositorNodeBrightContrast")
            output = tree.nodes.new("NodeGroupOutput")
            tree.interface.new_socket(
                name="Image",
                in_out="OUTPUT",
                socket_type="NodeSocketColor",
            )
        else:
            scene.use_nodes = True
            tree = scene.node_tree
            tree.nodes.clear()
            render_layers = tree.nodes.new("CompositorNodeRLayers")
            hue_sat = tree.nodes.new("CompositorNodeHueSat")
            bright_contrast = tree.nodes.new("CompositorNodeBrightContrast")
            output = tree.nodes.new("CompositorNodeComposite")

        hue_sat.inputs["Saturation"].default_value = 0.68
        hue_sat.inputs["Value"].default_value = 0.92
        bright_contrast.inputs["Bright"].default_value = -1.5
        bright_contrast.inputs["Contrast"].default_value = -4.0

        tree.links.new(render_layers.outputs["Image"], hue_sat.inputs["Image"])
        tree.links.new(hue_sat.outputs["Image"], bright_contrast.inputs["Image"])
        tree.links.new(bright_contrast.outputs["Image"], output.inputs["Image"])
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
    scene.view_settings.exposure = VARIANT["exposure"]

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
        panel_scale = VARIANT.get("panel_scale", (0.72, 0.16))
        panel.scale = (panel_scale[0], panel_scale[1], 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        panel.data.materials.append(emit_mat)

        bpy.ops.object.light_add(type="AREA", location=(x, y, CEILING_Z - 0.11))
        light = bpy.context.object
        light.name = f"AreaLight_{idx:02d}"
        light.data.energy = VARIANT["light_power"]
        light.data.shape = "RECTANGLE"
        area_size = VARIANT.get("area_size", (1.55, 0.45))
        light.data.size = area_size[0]
        light.data.size_y = area_size[1]
        light.data.color = VARIANT["light_color"]
        light["base_energy"] = VARIANT["light_power"]
        area_lights.append(light)

    bpy.ops.object.light_add(type="AREA", location=(-19.0, 1.3, 2.75))
    front_fill = bpy.context.object
    front_fill.name = "FrontFill_Area80"
    front_fill.data.energy = VARIANT["light_power"]
    front_fill.data.shape = "DISK"
    front_fill.data.size = 2.5
    point_camera(front_fill, (-10.0, -1.2, 1.0))
    area_lights.append(front_fill)

    # Aim diagonally down a long open sight line.  A 2D floor-plan probe gives
    # this pose ~31 m of center-ray depth while still keeping side walls in view.
    bpy.ops.object.camera_add(location=VARIANT["camera"])
    camera = bpy.context.object
    camera.name = "Camera_30mm"
    camera.data.lens = 30.0
    camera.data.sensor_width = 36.0
    point_camera(camera, VARIANT["target"])
    scene.camera = camera

    bpy.context.view_layer.update()

    # Geometry-level visibility diagnostic: a Backrooms view should have some
    # depth.  A center ray that hits a wall only a couple of metres away means
    # the camera is effectively plastered against a partition.
    depsgraph = bpy.context.evaluated_depsgraph_get()
    forward = camera.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0))
    hit, location, _normal, _face, _obj, _matrix = scene.ray_cast(
        depsgraph,
        camera.location,
        forward.normalized(),
    )
    center_ray_distance = (
        float((location - camera.location).length) if hit else float("inf")
    )
    print(f"BACKROOMS_CENTER_RAY_M={center_ray_distance:.3f}")

    compositor_grade = setup_color_grade(scene)
    return scene, camera, area_lights, walls, compositor_grade, center_ray_distance


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)
    scene, camera, area_lights, walls, compositor_grade, center_ray_distance = setup_scene()
    base_camera = camera.location.copy()

    frame_stats = []
    for frame in range(FRAME_START, FRAME_END + 1):
        t = (frame - FRAME_START) / max(1, FRAME_END - FRAME_START)
        camera.location = (
            base_camera.x + 0.72 * t,
            base_camera.y + 0.05 * math.sin(t * math.tau),
            base_camera.z + 0.015 * math.sin(t * math.tau * 0.5),
        )
        target = VARIANT["target"]
        point_camera(
            camera,
            (
                target[0] + 0.4 * t,
                target[1] + 0.04 * math.sin(t * math.tau),
                target[2],
            ),
        )

        for idx, light in enumerate(area_lights):
            phase = idx * 0.47
            flicker = 0.97 + 0.03 * math.sin(t * math.tau * 2.0 + phase)
            if idx == 5:
                flicker *= 0.86 + 0.14 * abs(math.sin(t * math.tau * 3.0))
            light.data.energy = VARIANT["light_power"] * flicker

        scene.frame_set(frame)
        bpy.context.view_layer.update()
        scene.render.filepath = str(FRAMES / f"frame_{frame:04d}.png")
        bpy.ops.render.render(write_still=True)
        frame_stats.append({
            "frame": frame,
            "camera": [round(float(v), 5) for v in camera.location],
            "flicker_light_w": round(float(area_lights[5].data.energy), 4),
        })

    preview_frame = 1 if VARIANT_SWEEP else (2 if FAST_PREVIEW else 12)
    shutil.copy2(FRAMES / f"frame_{preview_frame:04d}.png", OUT / "preview.png")

    report = {
        "experiment": EXPERIMENT,
        "fast_preview": FAST_PREVIEW,
        "variant_sweep": VARIANT_SWEEP,
        "variant_id": VARIANT_ID,
        "variant_name": VARIANT["name"],
        "variant_parameters": {
            "wall_scale": VARIANT.get("wall_scale", 7.5),
            "wall_detail": VARIANT.get("wall_detail", 3.0),
            "wall_bump": VARIANT.get("wall_bump", 0.16),
            "floor_scale": VARIANT.get("floor_scale", 38.0),
            "floor_bump": VARIANT.get("floor_bump", 0.38),
            "panel_scale": list(VARIANT.get("panel_scale", (0.72, 0.16))),
            "area_size": list(VARIANT.get("area_size", (1.55, 0.45))),
            "emission_strength": VARIANT.get("emission_strength", EMISSION_STRENGTH),
        },
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
        "center_ray_distance_m": round(center_ray_distance, 4),
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
    if not FAST_PREVIEW:
        bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f"{EXPERIMENT}.blend"))

    print(f"BACKROOMS_FAST_PREVIEW={int(FAST_PREVIEW)}")
    print(f"BACKROOMS_VARIANT={VARIANT_ID}:{VARIANT['name']}")
    print(f"BLENDER52_VERSION={bpy.app.version_string}")
    print(f"BLENDER52_ENGINE={scene.render.engine}")
    print(f"BLENDER52_FRAMES={report['frame_count']}")
    print(f"BACKROOMS_WALLS={report['wall_count']}")
    print(f"BACKROOMS_LIGHTS={report['area_light_count']}")


if __name__ == "__main__":
    main()
