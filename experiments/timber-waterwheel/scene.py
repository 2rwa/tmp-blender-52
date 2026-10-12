"""Blender 5.2 editable waterwheel model + 2 s turntable render."""
from __future__ import annotations

import json
import math
import shutil
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import CENTER_Z, PADDLE_COUNT, RADIUS, SPOKE_COUNT, RIM_SEGMENTS, create_model

EXPERIMENT = "timber-waterwheel"
OUT = Path("output52")
FRAMES = OUT / "frames"
FIRST = 1
LAST = 48
FPS = 24
RESOLUTION = (768, 432)
SPIN_RADIANS = math.pi * 0.75


def point_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def initialize():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.frame_start = FIRST
    scene.frame_end = LAST
    scene.render.fps = FPS
    scene.render.resolution_x, scene.render.resolution_y = RESOLUTION
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = engine
            break
        except (ValueError, TypeError):
            continue
    else:
        raise RuntimeError("Blender 5.2 EEVEE render engine unavailable")
    if hasattr(scene, "eevee"):
        try:
            scene.eevee.taa_render_samples = 32
        except AttributeError:
            pass

    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.15, 0.21, 0.26, 1.0)
    bg.inputs["Strength"].default_value = 0.46

    bpy.ops.object.light_add(type="SUN", location=(-5, -6, 10))
    sun = bpy.context.object
    sun.name = "Late afternoon sunlight"
    sun.rotation_euler = (math.radians(29), math.radians(-21), math.radians(-32))
    sun.data.energy = 2.0
    sun.data.angle = math.radians(4.5)

    bpy.ops.object.light_add(type="AREA", location=(2.0, -4.5, 8.4))
    fill = bpy.context.object
    fill.name = "Large soft photography light"
    fill.data.energy = 1250
    fill.data.shape = "DISK"
    fill.data.size = 6.0

    bpy.ops.object.camera_add(location=(8.0, -13.0, 8.1))
    camera = bpy.context.object
    camera.name = "Waterwheel three-quarter camera"
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 10.4
    point_at(camera, (-0.65, 0.0, 2.64))
    scene.camera = camera

    scene.render.film_transparent = False
    scene.camera.data.lens = 44
    return scene


def main():
    OUT.mkdir(exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)
    scene = initialize()
    wheel, counts = create_model()
    assert counts["paddle"] == PADDLE_COUNT
    assert counts["rim"] == 2 * RIM_SEGMENTS
    assert counts["spoke"] == 2 * SPOKE_COUNT

    # The assembly is real geometry, not a flattened mesh. Key every frame
    # to keep playback reproducible across Blender's animation curve versions.
    stats = []
    for frame in range(FIRST, LAST + 1):
        angle = SPIN_RADIANS * (frame - FIRST) / (LAST - FIRST)
        scene.frame_set(frame)
        wheel.rotation_euler[1] = angle
        wheel.keyframe_insert(data_path="rotation_euler", index=1, frame=frame)
        bpy.context.view_layer.update()
        scene.render.filepath = str(FRAMES / ("frame_%04d.png" % frame))
        bpy.ops.render.render(write_still=True)
        stats.append({"frame": frame, "wheel_angle_rad": round(angle, 7)})

    shutil.copy2(FRAMES / "frame_0014.png", OUT / "preview.png")
    scene.frame_set(14)
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / (EXPERIMENT + ".blend")))

    report = {
        "experiment": EXPERIMENT,
        "blender_version": bpy.app.version_string,
        "engine": scene.render.engine,
        "resolution": list(RESOLUTION),
        "frame_start": FIRST,
        "frame_end": LAST,
        "frame_count": LAST - FIRST + 1,
        "fps": FPS,
        "preview_frame": 14,
        "wheel_radius_m": RADIUS,
        "wheel_axis": "Y",
        "wheel_center_height_m": CENTER_Z,
        "wheel_component_counts": counts,
        "animation": "keyframed editable rotating assembly",
        "rotation_degrees": round(math.degrees(SPIN_RADIANS), 3),
        "mesh_objects": sum(1 for obj in bpy.data.objects if obj.type == "MESH"),
        "frame_stats": stats,
    }
    (OUT / (EXPERIMENT + "-report.json")).write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("WATERWHEEL_BLENDER_VERSION=" + bpy.app.version_string)
    print("WATERWHEEL_COMPONENTS=" + json.dumps(counts, sort_keys=True))
    print("WATERWHEEL_FRAMES=" + str(len(stats)))
    print("WATERWHEEL_MESH_OBJECTS=" + str(report["mesh_objects"]))


if __name__ == "__main__":
    main()
