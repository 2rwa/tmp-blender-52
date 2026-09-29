from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

import bpy
from mathutils import Vector

OUT = Path("output52")
FRAMES = OUT / "frames"
EXPERIMENT = "hello-blender52"

FRAME_START = 1
FRAME_END = 48
FPS = 24
RES_X = 480
RES_Y = 360


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


def choose_engine(scene: bpy.types.Scene) -> str:
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = engine
            return engine
        except Exception:
            continue
    raise RuntimeError("No EEVEE render engine available")


def make_material(name: str, color: tuple[float, float, float, float], metallic: float = 0.0):
    mat = bpy.data.materials.new(name=name)
    mat.diffuse_color = color
    mat.use_nodes = True
    principled = mat.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = 0.35
    principled.inputs["Metallic"].default_value = metallic
    return mat


def point_camera(camera: bpy.types.Object, target=(0.0, 0.0, 0.8)) -> None:
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def setup_scene() -> tuple[bpy.types.Scene, bpy.types.Object]:
    clear_scene()
    scene = bpy.context.scene
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    scene.render.fps = FPS
    scene.render.resolution_x = RES_X
    scene.render.resolution_y = RES_Y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    engine = choose_engine(scene)

    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.018, 0.025, 0.05, 1.0)
    bg.inputs["Strength"].default_value = 0.28

    bpy.ops.mesh.primitive_plane_add(size=12, location=(0.0, 0.0, 0.0))
    floor = bpy.context.object
    floor.data.materials.append(make_material("Floor", (0.08, 0.10, 0.16, 1.0), 0.05))

    bpy.ops.mesh.primitive_monkey_add(location=(0.0, 0.0, 1.25))
    hero = bpy.context.object
    hero.name = "Suzanne"
    hero.scale = (1.15, 1.15, 1.15)
    bpy.ops.object.shade_smooth()
    hero.data.materials.append(make_material("Hero", (0.12, 0.48, 0.95, 1.0), 0.35))

    bpy.ops.mesh.primitive_torus_add(
        major_radius=2.0,
        minor_radius=0.12,
        location=(0.0, 0.0, 1.25),
        rotation=(math.radians(90), 0.0, 0.0),
    )
    ring = bpy.context.object
    ring.name = "Ring"
    ring.data.materials.append(make_material("RingMat", (0.95, 0.34, 0.08, 1.0), 0.65))

    bpy.ops.object.light_add(type="AREA", location=(3.5, -3.0, 6.0))
    key = bpy.context.object
    key.data.energy = 900
    key.data.shape = "DISK"
    key.data.size = 4.0

    bpy.ops.object.light_add(type="AREA", location=(-4.0, 1.5, 3.0))
    fill = bpy.context.object
    fill.data.energy = 500
    fill.data.size = 3.0

    bpy.ops.object.camera_add(location=(6.2, -7.2, 4.2))
    camera = bpy.context.object
    point_camera(camera)
    camera.data.lens = 48
    scene.camera = camera

    hero["render_engine"] = engine
    return scene, hero


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)

    scene, hero = setup_scene()
    engine = scene.render.engine

    frame_stats = []
    for frame in range(FRAME_START, FRAME_END + 1):
        t = (frame - FRAME_START) / max(1, FRAME_END - FRAME_START)
        hero.rotation_euler = (
            math.radians(8.0) * math.sin(t * math.tau),
            t * math.tau * 1.2,
            t * math.tau * 0.55,
        )
        hero.location.z = 1.25 + 0.18 * math.sin(t * math.tau * 2.0)
        scene.frame_set(frame)
        bpy.context.view_layer.update()

        scene.render.filepath = str(FRAMES / f"frame_{frame:04d}.png")
        bpy.ops.render.render(write_still=True)

        frame_stats.append({
            "frame": frame,
            "rotation_y": float(hero.rotation_euler.y),
            "z": float(hero.location.z),
        })

    preview_frame = 24
    shutil.copy2(
        FRAMES / f"frame_{preview_frame:04d}.png",
        OUT / "preview.png",
    )

    report = {
        "experiment": EXPERIMENT,
        "blender_version": bpy.app.version_string,
        "engine": engine,
        "frame_start": FRAME_START,
        "frame_end": FRAME_END,
        "frame_count": FRAME_END - FRAME_START + 1,
        "fps": FPS,
        "resolution": [RES_X, RES_Y],
        "preview_frame": preview_frame,
        "frame_stats": frame_stats,
    }
    (OUT / f"{EXPERIMENT}-report.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f"{EXPERIMENT}.blend"))

    print(f"BLENDER52_VERSION={bpy.app.version_string}")
    print(f"BLENDER52_ENGINE={engine}")
    print(f"BLENDER52_FRAMES={report['frame_count']}")


if __name__ == "__main__":
    main()
