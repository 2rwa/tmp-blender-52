from __future__ import annotations

import json
import math
import shutil
import struct
import time
import urllib.request
import zlib
from pathlib import Path

import bpy
from mathutils import Vector

OUT = Path("output52")
FRAMES = OUT / "frames"
EXPERIMENT = "yokohama-terrain-workbench-wire"

# Low-resolution first pass: Yokohama City approximate bounding box.
LAT_MIN = 35.30
LAT_MAX = 35.60
LON_MIN = 139.47
LON_MAX = 139.78
DEM_ZOOM = 11
GRID_X = 96
GRID_Y = 112
FRAME_START = 1
FRAME_END = 144
FPS = 24
RES_X = 320
RES_Y = 180
EXAGGERATION_START = 1.0
EXAGGERATION_END = 32.0
TERRAIN_WIDTH_BU = 12.0
GSI_URL = "https://cyberjapandata.gsi.go.jp/xyz/dem_png/{z}/{x}/{y}.png"


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
    for engine in ("BLENDER_WORKBENCH", "BLENDER_WORKBENCH_NEXT"):
        try:
            scene.render.engine = engine
            return engine
        except Exception:
            continue
    raise RuntimeError("No Workbench render engine available")


def lonlat_to_tile_pixel(lon: float, lat: float, zoom: int) -> tuple[int, int, int, int]:
    n = 2 ** zoom
    xf = (lon + 180.0) / 360.0 * n
    lat_rad = math.radians(lat)
    yf = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
    tx = math.floor(xf)
    ty = math.floor(yf)
    px = min(255, max(0, int((xf - tx) * 256.0)))
    py = min(255, max(0, int((yf - ty) * 256.0)))
    return tx, ty, px, py


def decode_dem(rgb: tuple[int, int, int]) -> float | None:
    r, g, b = rgb
    x = (r << 16) | (g << 8) | b
    if x == (1 << 23):
        return None
    if x < (1 << 23):
        return x * 0.01
    return (x - (1 << 24)) * 0.01


def paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def decode_png_rgb(data: bytes) -> tuple[int, int, int, bytes]:
    signature = b"\x89PNG\r\n\x1a\n"
    if not data.startswith(signature):
        raise RuntimeError("DEM tile is not a PNG")

    pos = len(signature)
    width = height = bit_depth = color_type = interlace = None
    idat = bytearray()

    while pos + 12 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        chunk_type = data[pos + 4:pos + 8]
        chunk_data = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(
                ">IIBBBBB", chunk_data
            )
            if compression != 0 or filter_method != 0:
                raise RuntimeError("unsupported PNG compression/filter method")
        elif chunk_type == b"IDAT":
            idat.extend(chunk_data)
        elif chunk_type == b"IEND":
            break

    if width is None or height is None:
        raise RuntimeError("PNG missing IHDR")
    if bit_depth != 8 or color_type not in (2, 6) or interlace != 0:
        raise RuntimeError(
            f"unsupported PNG format: bit_depth={bit_depth}, color_type={color_type}, interlace={interlace}"
        )

    channels = 3 if color_type == 2 else 4
    stride = width * channels
    raw = zlib.decompress(bytes(idat))
    expected = height * (stride + 1)
    if len(raw) != expected:
        raise RuntimeError(f"unexpected PNG payload length: {len(raw)} != {expected}")

    pixels = bytearray(height * stride)
    previous = bytearray(stride)
    src = 0
    dst = 0

    for _ in range(height):
        filter_type = raw[src]
        src += 1
        scan = bytearray(raw[src:src + stride])
        src += stride

        for i in range(stride):
            left = scan[i - channels] if i >= channels else 0
            up = previous[i]
            up_left = previous[i - channels] if i >= channels else 0
            if filter_type == 0:
                value = scan[i]
            elif filter_type == 1:
                value = (scan[i] + left) & 0xFF
            elif filter_type == 2:
                value = (scan[i] + up) & 0xFF
            elif filter_type == 3:
                value = (scan[i] + ((left + up) >> 1)) & 0xFF
            elif filter_type == 4:
                value = (scan[i] + paeth(left, up, up_left)) & 0xFF
            else:
                raise RuntimeError(f"unsupported PNG filter type: {filter_type}")
            scan[i] = value

        pixels[dst:dst + stride] = scan
        previous = scan
        dst += stride

    return width, height, channels, bytes(pixels)


def tile_rgb(tile: tuple[int, int, int, bytes], px: int, py: int) -> tuple[int, int, int]:
    width, height, channels, pixels = tile
    if not (0 <= px < width and 0 <= py < height):
        raise IndexError((px, py))
    offset = (py * width + px) * channels
    return pixels[offset], pixels[offset + 1], pixels[offset + 2]


def download_tile(
    tx: int,
    ty: int,
    cache: dict[tuple[int, int], tuple[int, int, int, bytes]],
) -> tuple[int, int, int, bytes]:
    key = (tx, ty)
    if key in cache:
        return cache[key]

    url = GSI_URL.format(z=DEM_ZOOM, x=tx, y=ty)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "tmp-blender-52-yokohama-terrain-workbench-wire/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read()

    tile_path = OUT / "dem-tiles" / f"{DEM_ZOOM}-{tx}-{ty}.png"
    tile_path.parent.mkdir(parents=True, exist_ok=True)
    tile_path.write_bytes(data)

    tile = decode_png_rgb(data)
    if tile[0:2] != (256, 256):
        raise RuntimeError(f"unexpected DEM tile size for {url}: {tile[0:2]}")
    cache[key] = tile
    print(f"GSI_DEM_TILE={url}")
    return tile

def sample_dem() -> tuple[list[list[float | None]], dict]:
    cache: dict[tuple[int, int], tuple[int, int, int, bytes]] = {}
    heights: list[list[float | None]] = []
    valid: list[float] = []

    for iy in range(GRID_Y):
        fy = iy / max(1, GRID_Y - 1)
        lat = LAT_MIN + (LAT_MAX - LAT_MIN) * fy
        row: list[float | None] = []
        for ix in range(GRID_X):
            fx = ix / max(1, GRID_X - 1)
            lon = LON_MIN + (LON_MAX - LON_MIN) * fx
            tx, ty, px, py = lonlat_to_tile_pixel(lon, lat, DEM_ZOOM)
            image = download_tile(tx, ty, cache)
            value = decode_dem(tile_rgb(image, px, py))
            row.append(value)
            if value is not None:
                valid.append(value)
        heights.append(row)

    if not valid:
        raise RuntimeError("GSI DEM returned no valid elevation samples")

    report = {
        "tile_count": len(cache),
        "sample_count": GRID_X * GRID_Y,
        "valid_sample_count": len(valid),
        "valid_ratio": len(valid) / (GRID_X * GRID_Y),
        "elevation_min_m": min(valid),
        "elevation_max_m": max(valid),
        "elevation_mean_m": sum(valid) / len(valid),
    }
    return heights, report


def make_terrain_material(zmax: float):
    mat = bpy.data.materials.new(name="TerrainHeight")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    for node in list(nodes):
        nodes.remove(node)

    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    geometry = nodes.new("ShaderNodeNewGeometry")
    separate = nodes.new("ShaderNodeSeparateXYZ")
    ramp = nodes.new("ShaderNodeValToRGB")
    map_range = nodes.new("ShaderNodeMapRange")

    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.055, 0.12, 0.055, 1.0)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (0.62, 0.46, 0.24, 1.0)
    mid = ramp.color_ramp.elements.new(0.42)
    mid.color = (0.18, 0.34, 0.11, 1.0)

    map_range.inputs["From Min"].default_value = -0.05
    map_range.inputs["From Max"].default_value = max(0.1, zmax)
    links.new(geometry.outputs["Position"], separate.inputs["Vector"])
    links.new(separate.outputs["Z"], map_range.inputs["Value"])
    links.new(map_range.outputs["Result"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    bsdf.inputs["Roughness"].default_value = 0.78
    mat.diffuse_color = (0.18, 0.34, 0.11, 1.0)
    return mat


def make_simple_material(name: str, color: tuple[float, float, float, float], roughness: float):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    principled = mat.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = roughness
    mat.diffuse_color = color
    return mat


def build_terrain(heights: list[list[float | None]]) -> tuple[bpy.types.Object, dict]:
    mid_lat = (LAT_MIN + LAT_MAX) * 0.5
    width_m = (LON_MAX - LON_MIN) * 111_320.0 * math.cos(math.radians(mid_lat))
    height_m = (LAT_MAX - LAT_MIN) * 111_320.0
    terrain_depth_bu = TERRAIN_WIDTH_BU * height_m / width_m
    xy_scale = TERRAIN_WIDTH_BU / width_m

    valid_values = [h for row in heights for h in row if h is not None]
    zmax = max(valid_values) * xy_scale * EXAGGERATION_END

    verts = []
    faces = []
    for iy, row in enumerate(heights):
        fy = iy / max(1, GRID_Y - 1)
        y = (fy - 0.5) * terrain_depth_bu
        for ix, elevation in enumerate(row):
            fx = ix / max(1, GRID_X - 1)
            x = (fx - 0.5) * TERRAIN_WIDTH_BU
            h = -25.0 if elevation is None else elevation
            z = h * xy_scale * EXAGGERATION_START
            verts.append((x, y, z))

    for iy in range(GRID_Y - 1):
        for ix in range(GRID_X - 1):
            a = iy * GRID_X + ix
            b = a + 1
            c = a + GRID_X + 1
            d = a + GRID_X
            faces.append((a, b, c, d))

    mesh = bpy.data.meshes.new("YokohamaTerrainMesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    terrain = bpy.data.objects.new("YokohamaTerrain", mesh)
    bpy.context.collection.objects.link(terrain)
    terrain.data.materials.append(make_terrain_material(zmax))
    terrain.display_type = "WIRE"
    terrain.show_wire = True
    terrain.show_all_edges = True
    for poly in mesh.polygons:
        poly.use_smooth = True

    return terrain, {
        "width_m": width_m,
        "height_m": height_m,
        "terrain_width_bu": TERRAIN_WIDTH_BU,
        "terrain_depth_bu": terrain_depth_bu,
        "zmax_bu": zmax,
    }


def point_camera(camera: bpy.types.Object, target=(0.0, 0.0, 0.25)) -> None:
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def setup_scene(heights: list[list[float | None]]) -> tuple[bpy.types.Scene, bpy.types.Object, bpy.types.Object, dict]:
    clear_scene()
    scene = bpy.context.scene
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    scene.render.fps = FPS
    scene.render.resolution_x = RES_X
    scene.render.resolution_y = RES_Y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    engine = choose_engine(scene)
    shading = scene.display.shading
    if hasattr(shading, "type"):
        shading.type = "WIREFRAME"
    if hasattr(shading, "light"):
        shading.light = "FLAT"
    if hasattr(shading, "color_type"):
        shading.color_type = "SINGLE"
    if hasattr(shading, "single_color"):
        shading.single_color = (0.72, 0.88, 1.0)
    if hasattr(shading, "show_shadows"):
        shading.show_shadows = False
    if hasattr(shading, "show_cavity"):
        shading.show_cavity = False
    if hasattr(shading, "show_specular_highlight"):
        shading.show_specular_highlight = False
    if hasattr(shading, "show_wireframes"):
        shading.show_wireframes = True
    if hasattr(shading, "background_type"):
        shading.background_type = "VIEWPORT"
    if hasattr(shading, "background_color"):
        shading.background_color = (0.01, 0.015, 0.025)
    print(f"WORKBENCH_SHADING_TYPE={getattr(shading, 'type', 'unknown')}")

    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.035, 0.055, 0.08, 1.0)
    bg.inputs["Strength"].default_value = 0.55

    terrain, terrain_metrics = build_terrain(heights)

    water_depth = terrain_metrics["terrain_depth_bu"] + 3.0
    bpy.ops.mesh.primitive_plane_add(size=2.0, location=(0.0, 0.0, -0.002))
    water = bpy.context.object
    water.name = "TokyoBayWater"
    water.scale = ((TERRAIN_WIDTH_BU + 3.0) * 0.5, water_depth * 0.5, 1.0)
    water.data.materials.append(make_simple_material("Water", (0.025, 0.15, 0.24, 1.0), 0.32))
    water.hide_render = True

    bpy.ops.mesh.primitive_cube_add(
        location=(0.0, 0.0, -0.18),
        scale=((TERRAIN_WIDTH_BU + 0.4) * 0.5, (terrain_metrics["terrain_depth_bu"] + 0.4) * 0.5, 0.17),
    )
    base = bpy.context.object
    base.name = "TerrainBase"
    base.data.materials.append(make_simple_material("Base", (0.045, 0.052, 0.046, 1.0), 0.9))
    base.hide_render = True

    bpy.ops.object.light_add(type="SUN", location=(4.0, -6.0, 10.0))
    sun = bpy.context.object
    sun.name = "MorningSun"
    sun.rotation_euler = (math.radians(28), math.radians(-18), math.radians(-32))
    sun.data.energy = 3.0
    sun.data.angle = math.radians(10.0)

    bpy.ops.object.light_add(type="AREA", location=(-5.0, -2.0, 8.0))
    fill = bpy.context.object
    fill.data.energy = 650
    fill.data.shape = "DISK"
    fill.data.size = 7.0

    bpy.ops.object.camera_add(location=(11.5, -14.0, 11.0))
    camera = bpy.context.object
    camera.name = "YokohamaOverviewCamera"
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 18.0
    point_camera(camera, (0.0, 0.0, 0.18))
    scene.camera = camera

    terrain["render_engine"] = engine
    return scene, camera, terrain, terrain_metrics


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)

    heights, dem_report = sample_dem()
    scene, camera, terrain, terrain_metrics = setup_scene(heights)
    engine = scene.render.engine

    frame_stats = []
    render_loop_started = time.perf_counter()
    initial = Vector(camera.location)
    radius = math.hypot(initial.x, initial.y)
    base_angle = math.atan2(initial.y, initial.x)

    for frame in range(FRAME_START, FRAME_END + 1):
        t = (frame - FRAME_START) / max(1, FRAME_END - FRAME_START)
        exaggeration = EXAGGERATION_START * ((EXAGGERATION_END / EXAGGERATION_START) ** t)
        terrain.scale.z = exaggeration / EXAGGERATION_START
        angle = base_angle + math.radians(16.0) * (t - 0.5)
        camera.location.x = radius * math.cos(angle)
        camera.location.y = radius * math.sin(angle)
        camera.location.z = initial.z + 0.35 * math.sin(t * math.pi)
        point_camera(camera, (0.0, 0.0, 0.18))
        scene.frame_set(frame)
        bpy.context.view_layer.update()

        scene.render.filepath = str(FRAMES / f"frame_{frame:04d}.png")
        frame_started = time.perf_counter()
        bpy.ops.render.render(write_still=True)
        frame_seconds = time.perf_counter() - frame_started
        frame_stats.append({
            "frame": frame,
            "exaggeration": round(exaggeration, 6),
            "render_seconds": round(frame_seconds, 6),
            "camera": [round(float(v), 5) for v in camera.location],
        })

    render_loop_seconds = time.perf_counter() - render_loop_started
    preview_frame = FRAME_END
    shutil.copy2(FRAMES / f"frame_{preview_frame:04d}.png", OUT / "preview.png")

    report_frame_count = FRAME_END - FRAME_START + 1
    report = {
        "experiment": EXPERIMENT,
        "title": "Yokohama City terrain Workbench wireframe, 1x to 32x",
        "display_mode": "wireframe",
        "blender_version": bpy.app.version_string,
        "engine": engine,
        "data_source": "Geospatial Information Authority of Japan (GSI) DEM10B PNG elevation tiles",
        "data_source_url_template": GSI_URL,
        "bbox_lonlat": [LON_MIN, LAT_MIN, LON_MAX, LAT_MAX],
        "dem_zoom": DEM_ZOOM,
        "grid": [GRID_X, GRID_Y],
        "vertical_exaggeration": {
            "start": EXAGGERATION_START,
            "end": EXAGGERATION_END,
            "progression": "exponential",
        },
        "frame_start": FRAME_START,
        "frame_end": FRAME_END,
        "frame_count": report_frame_count,
        "fps": FPS,
        "resolution": [RES_X, RES_Y],
        "preview_frame": preview_frame,
        "render_loop_seconds": render_loop_seconds,
        "seconds_per_frame": render_loop_seconds / report_frame_count,
        "dem": dem_report,
        "terrain": terrain_metrics,
        "frame_stats": frame_stats,
    }
    (OUT / f"{EXPERIMENT}-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f"{EXPERIMENT}.blend"))

    print(f"BLENDER52_VERSION={bpy.app.version_string}")
    print(f"BLENDER52_ENGINE={engine}")
    print(f"YOKOHAMA_DEM_VALID_RATIO={dem_report['valid_ratio']:.4f}")
    print(f"YOKOHAMA_ELEVATION_RANGE={dem_report['elevation_min_m']:.2f}..{dem_report['elevation_max_m']:.2f}")
    print(f"BLENDER52_FRAMES={report['frame_count']}")
    print(f"WORKBENCH_RENDER_LOOP_SECONDS={render_loop_seconds:.6f}")
    print(f"WORKBENCH_SECONDS_PER_FRAME={render_loop_seconds / report_frame_count:.6f}")
    print("WORKBENCH_DISPLAY_MODE=wireframe")


if __name__ == "__main__":
    main()
