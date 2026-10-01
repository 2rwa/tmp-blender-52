from __future__ import annotations

import hashlib
import json
import math
import shutil
import time
from pathlib import Path

import bpy
from mathutils import Vector

OUT = Path("output52")
FRAMES = OUT / "frames"
EXPERIMENT = "sail-ship-wire-hd"
SOURCE = Path("Sail ship.blend").resolve()
EXPECTED_SOURCE_SHA256 = "f9cf8bb0fc345b3851e9fd596fc75edf236b32309e1a6ce193e8c2a9b25aff78"
RES_X = 1280
RES_Y = 720
FRAME_START = 1
FRAME_END = 240
FPS = 24
DURATION_SECONDS = 10


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def choose_engine(scene: bpy.types.Scene) -> str:
    for engine in ("BLENDER_WORKBENCH", "BLENDER_WORKBENCH_NEXT"):
        try:
            scene.render.engine = engine
            return engine
        except Exception:
            continue
    raise RuntimeError("No Workbench render engine available")


def world_bounds() -> tuple[list[Vector], Vector, Vector, Vector, int]:
    points: list[Vector] = []
    count = 0
    supported = {"MESH", "CURVE", "SURFACE", "META", "FONT"}
    for obj in bpy.context.scene.objects:
        if obj.type not in supported or obj.hide_render:
            continue
        try:
            corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        except Exception:
            continue
        if not corners:
            continue
        points.extend(corners)
        count += 1

    if not points:
        raise RuntimeError("No renderable ship geometry found in Sail ship.blend")

    minimum = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maximum = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    center = (minimum + maximum) * 0.5
    return points, minimum, maximum, center, count


def point_camera(camera: bpy.types.Object, target: Vector) -> None:
    direction = target - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def make_orbit_camera(center: Vector, span: Vector) -> tuple[bpy.types.Object, float, float]:
    max_dim = max(span.x, span.y, span.z, 1.0e-4)
    orbit_radius = max_dim * 3.0
    orbit_height = max_dim * 1.1

    camera_data = bpy.data.cameras.new("SailShipWireCamera")
    camera = bpy.data.objects.new("SailShipWireCamera", camera_data)
    bpy.context.scene.collection.objects.link(camera)

    camera.data.type = "ORTHO"
    camera.data.ortho_scale = max_dim * 1.80
    camera.data.clip_start = max(max_dim * 0.001, 0.001)
    camera.data.clip_end = max_dim * 20.0

    camera.location = center + Vector((orbit_radius, 0.0, orbit_height))
    point_camera(camera, center)
    bpy.context.view_layer.update()
    return camera, orbit_radius, orbit_height


def add_wireframe_geometry(span: Vector) -> tuple[int, int, float]:
    max_dim = max(span.x, span.y, span.z, 1.0e-4)
    world_thickness = max_dim * 0.00125
    mesh_count = 0
    edge_count = 0

    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or obj.hide_render:
            continue
        mesh_count += 1
        edge_count += len(obj.data.edges)

        scale_values = [abs(float(v)) for v in obj.scale if abs(float(v)) > 1.0e-6]
        object_scale = sum(scale_values) / len(scale_values) if scale_values else 1.0

        wire = obj.modifiers.new(name="HDWireframeGeometry", type="WIREFRAME")
        wire.thickness = world_thickness / object_scale
        wire.use_replace = True
        wire.use_boundary = True
        wire.use_even_offset = True

    if mesh_count == 0:
        raise RuntimeError("No mesh objects available for wireframe geometry")
    return mesh_count, edge_count, world_thickness


def configure_workbench(scene: bpy.types.Scene) -> str:
    engine = choose_engine(scene)
    scene.render.resolution_x = RES_X
    scene.render.resolution_y = RES_Y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.fps = FPS
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END

    shading = scene.display.shading
    shading.type = "SOLID"
    if hasattr(shading, "light"):
        shading.light = "FLAT"
    if hasattr(shading, "color_type"):
        shading.color_type = "SINGLE"
    if hasattr(shading, "single_color"):
        shading.single_color = (0.86, 0.91, 1.0)
    if hasattr(shading, "show_shadows"):
        shading.show_shadows = False
    if hasattr(shading, "show_cavity"):
        shading.show_cavity = False
    if hasattr(shading, "show_specular_highlight"):
        shading.show_specular_highlight = False
    if hasattr(shading, "show_wireframes"):
        shading.show_wireframes = False
    if hasattr(shading, "background_type"):
        shading.background_type = "VIEWPORT"
    if hasattr(shading, "background_color"):
        shading.background_color = (0.018, 0.024, 0.038)

    scene.world.color = (0.018, 0.024, 0.038)
    return engine


def main() -> None:
    if not SOURCE.is_file():
        raise RuntimeError(f"Missing source blend: {SOURCE}")
    source_hash = sha256(SOURCE)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(f"Unexpected Sail ship.blend SHA-256: {source_hash}")

    OUT.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene

    points, minimum, maximum, center, object_count = world_bounds()
    span = maximum - minimum
    mesh_count, edge_count, wire_thickness = add_wireframe_geometry(span)
    engine = configure_workbench(scene)

    camera, orbit_radius, orbit_height = make_orbit_camera(center, span)
    scene.camera = camera
    bpy.context.view_layer.update()

    frame_count = FRAME_END - FRAME_START + 1
    started = time.perf_counter()

    for frame in range(FRAME_START, FRAME_END + 1):
        phase = (frame - FRAME_START) / frame_count
        angle = math.tau * phase
        camera.location = center + Vector((
            math.cos(angle) * orbit_radius,
            math.sin(angle) * orbit_radius,
            orbit_height,
        ))
        point_camera(camera, center)
        scene.frame_set(frame)
        scene.render.filepath = str(FRAMES / f"frame_{frame:04d}.png")
        bpy.context.view_layer.update()
        bpy.ops.render.render(write_still=True)

    render_seconds = time.perf_counter() - started

    first_frame = FRAMES / "frame_0001.png"
    if not first_frame.is_file() or first_frame.stat().st_size < 2_000:
        raise RuntimeError("Workbench render did not create a usable PNG")

    shutil.copy2(first_frame, OUT / "preview.png")

    output_blend = OUT / f"{EXPERIMENT}.blend"
    shutil.copy2(SOURCE, output_blend)

    report = {
        "experiment": EXPERIMENT,
        "title": "Sail Ship — Workbench Wireframe HD Turntable",
        "blender_version": bpy.app.version_string,
        "engine": engine,
        "display_mode": "wireframe",
        "wireframe_method": "geometry_modifier",
        "wireframe_world_thickness": round(wire_thickness, 8),
        "resolution": [RES_X, RES_Y],
        "frame_start": FRAME_START,
        "frame_end": FRAME_END,
        "frame_count": frame_count,
        "fps": FPS,
        "duration_seconds": DURATION_SECONDS,
        "orbit_degrees": 360,
        "orbit_radius": round(float(orbit_radius), 6),
        "orbit_height": round(float(orbit_height), 6),
        "source": "Sail ship.blend",
        "source_size_bytes": SOURCE.stat().st_size,
        "source_sha256": source_hash,
        "renderable_object_count": object_count,
        "mesh_object_count": mesh_count,
        "source_edge_count": edge_count,
        "bounds_min": [round(float(v), 6) for v in minimum],
        "bounds_max": [round(float(v), 6) for v in maximum],
        "bounds_span": [round(float(v), 6) for v in span],
        "camera_ortho_scale": round(float(camera.data.ortho_scale), 6),
        "render_seconds": round(render_seconds, 6),
        "seconds_per_frame": round(render_seconds / frame_count, 6),
        "note": "240 actual Blender Workbench wireframe renders; camera orbits the ship once over 10 seconds.",
    }
    (OUT / f"{EXPERIMENT}-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"BLENDER52_VERSION={bpy.app.version_string}")
    print(f"BLENDER52_ENGINE={engine}")
    print(f"SAIL_SHIP_SOURCE_SHA256={source_hash}")
    print(f"SAIL_SHIP_OBJECTS={object_count}")
    print(f"SAIL_SHIP_MESHES={mesh_count}")
    print(f"SAIL_SHIP_EDGES={edge_count}")
    print(f"WIRE_THICKNESS={wire_thickness:.8f}")
    print(f"WORKBENCH_RENDER_SECONDS={render_seconds:.6f}")
    print(f"WORKBENCH_SECONDS_PER_FRAME={render_seconds / frame_count:.6f}")


if __name__ == "__main__":
    main()
