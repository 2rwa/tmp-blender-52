from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import bpy
from mathutils import Vector

VARIANT = int(os.environ.get("TROPICAL_VARIANT", "1"))
OUT = Path(os.environ.get("TROPICAL_OUTPUT", f"sweep-output/v{VARIANT:02d}"))
BASE_SCENE = Path(__file__).resolve().parents[1] / "tropical-resort-coast-still" / "scene.py"

spec = importlib.util.spec_from_file_location("tropical_base_scene", BASE_SCENE)
base = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(base)

base.OUT = OUT
base.FRAMES = OUT / "frames"
base.EXPERIMENT = f"tropical-resort-sweep-v{VARIANT:02d}"
base.RES_X = 640
base.RES_Y = 360
base.SAMPLES = 10

BASE_CREATE_OCEAN = base.create_ocean
BASE_SETUP_CAMERA = base.setup_camera

VARIANTS = {
    1: {"name": "baseline-pass4", "description": "Pass 4 baseline."},
    2: {"name": "no-water-control", "description": "Hide the water surface completely.", "hide_water": True},
    3: {"name": "flat-water-geometry", "description": "Flatten all water geometry to z=0.", "flat_water": True},
    4: {"name": "clear-glass-no-depth-tint", "description": "Nearly clear constant transmissive water.", "material": "clear"},
    5: {"name": "constant-cyan-no-depth-tint", "description": "Constant cyan transmissive water.", "material": "cyan"},
    6: {"name": "short-water-650m", "description": "Move far water edge to 650 m.", "far_y": 650.0},
    7: {"name": "mid-water-900m", "description": "Move far water edge to 900 m.", "far_y": 900.0},
    8: {"name": "long-water-3000m", "description": "Push far water edge to 3000 m.", "far_y": 3000.0},
    9: {"name": "high-overview-camera", "description": "Higher camera looking down across lagoon.", "camera": "high"},
    10: {"name": "low-horizon-camera", "description": "Lower camera aimed closer to horizon.", "camera": "low"},
}
CFG = VARIANTS.get(VARIANT, VARIANTS[1])


def set_input(node, name: str, value) -> None:
    socket = node.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def constant_water_material(kind: str):
    mat = bpy.data.materials.new(f"SweepWater_{kind}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    if kind == "clear":
        set_input(bsdf, "Base Color", (0.88, 0.97, 0.98, 1.0))
        set_input(bsdf, "Transmission Weight", 0.995)
        set_input(bsdf, "Roughness", 0.018)
    else:
        set_input(bsdf, "Base Color", (0.055, 0.48, 0.53, 1.0))
        set_input(bsdf, "Transmission Weight", 0.92)
        set_input(bsdf, "Roughness", 0.032)
    set_input(bsdf, "IOR", 1.333)
    set_input(bsdf, "Metallic", 0.0)
    mat.node_tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def adjusted_create_ocean():
    ocean, settings = BASE_CREATE_OCEAN()

    if CFG.get("hide_water"):
        ocean.hide_render = True
        settings["diagnostic"] = "water-hidden"

    if CFG.get("flat_water"):
        for vertex in ocean.data.vertices:
            vertex.co.z = 0.0
        ocean.data.update()
        settings["diagnostic"] = "flat-water-z0"

    material_kind = CFG.get("material")
    if material_kind:
        ocean.data.materials.clear()
        ocean.data.materials.append(constant_water_material(material_kind))
        settings["diagnostic_material"] = material_kind

    target_far = CFG.get("far_y")
    if target_far:
        source_far = float(settings.get("far_y_m", 1450.0))
        for vertex in ocean.data.vertices:
            x = float(vertex.co.x)
            shore = base.shoreline_y(x) + 0.45
            denom = source_far - shore
            if abs(denom) < 1e-6:
                continue
            u = (float(vertex.co.y) - shore) / denom
            vertex.co.y = shore + u * (float(target_far) - shore)
        ocean.data.update()
        settings["far_y_m"] = float(target_far)
        settings["diagnostic"] = f"far-y-{target_far:g}"

    return ocean, settings


def adjusted_setup_camera(scene):
    mode = CFG.get("camera")
    if not mode:
        return BASE_SETUP_CAMERA(scene)

    if mode == "high":
        location = (58.0, -120.0, 42.0)
        target = (-18.0, 140.0, -2.5)
        lens = 52.0
    else:
        location = (42.0, -105.0, 7.0)
        target = (-12.0, 190.0, 0.0)
        lens = 48.0

    bpy.ops.object.camera_add(location=location)
    camera = bpy.context.object
    camera.name = f"SweepCamera_{mode}"
    camera.data.lens = lens
    camera.data.sensor_width = 36.0
    camera.data.clip_start = 0.1
    camera.data.clip_end = 5000.0
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    return camera


base.create_ocean = adjusted_create_ocean
base.setup_camera = adjusted_setup_camera


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    base.main()

    report_path = OUT / f"{base.EXPERIMENT}-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["sweep_variant"] = VARIANT
    report["sweep_name"] = CFG["name"]
    report["sweep_description"] = CFG["description"]
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    (OUT / "variant.json").write_text(
        json.dumps(
            {
                "variant": VARIANT,
                "name": CFG["name"],
                "description": CFG["description"],
                "resolution": [base.RES_X, base.RES_Y],
                "samples": base.SAMPLES,
            },
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )
    print(f"TROPICAL_SWEEP_VARIANT={VARIANT}:{CFG['name']}")


if __name__ == "__main__":
    main()
