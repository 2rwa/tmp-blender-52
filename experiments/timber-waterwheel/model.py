"""Procedural Japanese-style timber waterwheel and riverside diorama.

The wheel is assembled as independent editable meshes under a rotating Empty.
Dimensions are in approximate metres. Blender 5.2 / no external assets.
"""
import math
import random

import bpy
from mathutils import Vector

RADIUS = 2.16
CENTER_Z = 2.88
SPOKE_COUNT = 12
PADDLE_COUNT = 16
RIM_SEGMENTS = 24


def material(name, color, roughness=0.7, metallic=0.0, grain=False):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if grain:
        coord = nodes.new("ShaderNodeTexCoord")
        mapping = nodes.new("ShaderNodeVectorMath")
        mapping.operation = "MULTIPLY"
        mapping.inputs[1].default_value = (5.0, 1.0, 1.0)
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 5.5
        noise.inputs["Detail"].default_value = 3.0
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.21
        ramp.color_ramp.elements[0].color = tuple(c * 0.49 for c in color) + (1.0,)
        ramp.color_ramp.elements[1].position = 0.79
        ramp.color_ramp.elements[1].color = tuple(min(1.0, c * 1.36) for c in color) + (1.0,)
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.11
        bump.inputs["Distance"].default_value = 0.028
        links.new(coord.outputs["Generated"], mapping.inputs[0])
        links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
        links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def box(name, loc, size, mat, parent=None, rotation=None, bevel=0.025, role=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if rotation is not None:
        obj.rotation_euler = rotation
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Softened timber edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new("Weighted surface normals", "WEIGHTED_NORMAL")
    if parent is not None:
        obj.parent = parent
    if role:
        obj["wheel_component"] = role
    return obj


def beam(name, a, b, width, depth, mat, parent=None, role=None):
    direction = Vector(b) - Vector(a)
    mid = (Vector(a) + Vector(b)) / 2
    obj = box(name, mid, (width, depth, direction.length), mat, parent, role=role)
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    return obj


def cylinder(name, loc, radius, length, mat, parent=None, vertices=32, role=None):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=length,
        location=loc, rotation=(math.pi / 2, 0, 0),
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    if parent is not None:
        obj.parent = parent
    if role:
        obj["wheel_component"] = role
    bevel = obj.modifiers.new("Rounded machined edge", "BEVEL")
    bevel.width = 0.023
    bevel.segments = 2
    obj.modifiers.new("Weighted cylinder normals", "WEIGHTED_NORMAL")
    return obj


def water_mesh(name, grid, mat):
    verts, faces = grid
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    for poly in mesh.polygons:
        poly.use_smooth = True
    return obj


def build_wheel(wood, dark, iron, warm):
    root = bpy.data.objects.new("WHEEL / rotate Y (editable assembly)", None)
    bpy.context.collection.objects.link(root)
    root.location = (0, 0, CENTER_Z)
    root.rotation_mode = "XYZ"
    root["wheel_radius_m"] = RADIUS
    root["paddle_count"] = PADDLE_COUNT

    for side, y in enumerate((-0.49, 0.49), start=1):
        for i in range(RIM_SEGMENTS):
            a = math.tau * i / RIM_SEGMENTS
            b = math.tau * (i + 1) / RIM_SEGMENTS
            p = (RADIUS * math.cos(a), y, RADIUS * math.sin(a))
            q = (RADIUS * math.cos(b), y, RADIUS * math.sin(b))
            beam("Rim %d segment %02d" % (side, i), p, q,
                 0.23, 0.21, wood, root, "rim")
        for i in range(SPOKE_COUNT):
            a = math.tau * i / SPOKE_COUNT
            endpoint = (1.95 * math.cos(a), y, 1.95 * math.sin(a))
            beam("Spoke %d-%02d" % (side, i),
                 (0, y, 0), endpoint, 0.135, 0.13, dark, root, "spoke")
        cylinder("Timber hub %d" % side, (0, y, 0),
                 0.41, 0.30, warm, root, role="hub")

    for i in range(PADDLE_COUNT):
        a = math.tau * i / PADDLE_COUNT
        ca, sa = math.cos(a), math.sin(a)
        rot = (0, -a - math.pi / 2, 0)
        box("Scoop %02d broad blade" % i,
            (2.19 * ca, 0, 2.19 * sa),
            (0.78, 1.21, 0.105), wood, root, rot, role="paddle")
        box("Scoop %02d outer lip" % i,
            (2.34 * ca, 0, 2.34 * sa),
            (0.16, 1.21, 0.29), dark, root, rot, role="lip")
        for side, y in enumerate((-0.57, 0.57)):
            cylinder("Scoop bolt %02d-%d" % (i, side),
                     (2.15 * ca, y, 2.15 * sa),
                     0.045, 0.04, iron, root, vertices=12, role="bolt")

    cylinder("Continuous wrought iron axle", (0, 0, 0),
             0.20, 3.8, iron, root, role="axle")
    cylinder("Core timber barrel", (0, 0, 0),
             0.24, 1.45, dark, root, role="hub")

    counts = {}
    for obj in root.children:
        role = obj.get("wheel_component")
        if role:
            counts[role] = counts.get(role, 0) + 1
    return root, counts


def make_river(water):
    verts, faces = [], []
    nx, ny = 54, 22
    for j in range(ny):
        y = -3.3 + j * 6.6 / (ny - 1)
        for i in range(nx):
            x = -7 + i * 14 / (nx - 1)
            z = 0.07 + 0.041 * math.sin(x * 3.1 + y * 0.7)
            z += 0.018 * math.sin(x * 8.4 - y * 4.2)
            verts.append((x, y, z))
    for j in range(ny - 1):
        for i in range(nx - 1):
            n = j * nx + i
            faces.append((n, n + 1, n + nx + 1, n + nx))
    return water_mesh("Flowing turquoise river / surface", (verts, faces), water)


def make_waterfall(water):
    verts, faces = [], []
    # Curved falling sheet from the open flume toward top-left wheel buckets.
    along, across = 23, 7
    for i in range(along):
        t = i / (along - 1)
        for j in range(across):
            s = 2 * j / (across - 1) - 1
            x = -1.00 - 0.23 * t + 0.03 * math.sin(22 * t + 5 * s)
            y = 0.46 * s + 0.025 * math.sin(11 * t + s * 5)
            z = 5.20 - 0.76 * t ** 1.45 + 0.023 * math.sin(23 * t + s * 3)
            verts.append((x, y, z))
    for i in range(along - 1):
        for j in range(across - 1):
            n = i * across + j
            faces.append((n, n + across, n + across + 1, n + 1))
    water_mesh("Flume waterfall / sculpted sheet", (verts, faces), water)


def make_landscape(stone, moss, grass, water):
    box("Diorama footing", (0, 0, -0.40), (14.0, 9.0, 0.70), stone, bevel=0.20)
    for y in (-3.80, 3.80):
        box("Riverbank %+.1f" % y, (0, y, 0.01), (14.0, 1.7, 0.45),
            moss, bevel=0.13)
    make_river(water)
    rng = random.Random(52)
    for i in range(22):
        x = rng.uniform(-6.6, 6.6)
        y = rng.choice([-1, 1]) * rng.uniform(2.95, 3.85)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1.0,
                                              location=(x, y, 0.26))
        obj = bpy.context.object
        obj.name = "Natural river stone %02d" % i
        obj.scale = (rng.uniform(0.18, 0.50),
                     rng.uniform(0.16, 0.43), rng.uniform(0.14, 0.32))
        obj.rotation_euler[2] = rng.uniform(0, math.tau)
        obj.data.materials.append(stone)
    for i in range(18):
        x = rng.uniform(-6.7, 6.7)
        y = rng.choice([-1, 1]) * rng.uniform(3.38, 4.25)
        for n in range(2):
            bpy.ops.mesh.primitive_cone_add(vertices=5, radius1=0.085,
                                            radius2=0.0, depth=rng.uniform(0.20, 0.43),
                                            location=(x + n * 0.07, y, 0.32))
            bpy.context.object.name = "Reed %02d-%d" % (i, n)
            bpy.context.object.data.materials.append(grass)


def make_mill_support(stone, dark, iron):
    for side, y in enumerate((-1.46, 1.46)):
        box("Stone axle pier %d" % side,
            (0, y, 1.45), (0.75, 0.70, 2.65), stone, bevel=0.07)
        box("Cross-grain bearing seat %d" % side,
            (0, y, 2.83), (0.88, 0.88, 0.27), dark, bevel=0.045)
        cylinder("Bearing iron collar %d" % side,
                 (0, y, CENTER_Z), 0.31, 0.16, iron)
    for side, y in enumerate((-1.47, 1.47)):
        beam("Pier brace %d" % side, (0, y, 1.68), (0.85, y, 0.65),
             0.19, 0.19, dark)


def make_flume(wood, dark, water):
    length = 4.6
    cx = -3.27
    box("Elevated aqueduct / bottom", (cx, 0, 5.10),
        (length, 1.45, 0.18), wood, bevel=0.05)
    for side, y in enumerate((-0.69, 0.69)):
        box("Aqueduct side wall %d" % side, (cx, y, 5.38),
            (length, 0.16, 0.52), dark, bevel=0.035)
        for x in (-4.73, -2.56):
            beam("Flume trestle %.2f %d" % (x, side),
                 (x, y, 0.33), (x, y, 5.00), 0.19, 0.19, dark)
    box("Flume visible surface", (cx, 0, 5.215),
        (length-0.22, 1.16, 0.025), water, bevel=0.0)
    make_waterfall(water)


def create_model():
    wood = material("01 Honey-brown aged cedar", (0.43, 0.228, 0.095), grain=True)
    dark = material("02 Dark oiled structural timber", (0.22, 0.103, 0.044), grain=True)
    warm = material("03 Pale end grain", (0.61, 0.34, 0.13), grain=True)
    iron = material("04 Weathered iron hardware", (0.19, 0.21, 0.21),
                    roughness=0.42, metallic=0.76)
    stone = material("05 Granite and river stone", (0.34, 0.37, 0.39), roughness=0.95)
    moss = material("06 Mossy bank", (0.17, 0.245, 0.12), roughness=0.98)
    grass = material("07 Waterside reeds", (0.29, 0.40, 0.10), roughness=0.91)
    water = material("08 Jade river water", (0.055, 0.35, 0.43), roughness=0.26)
    root, counts = build_wheel(wood, dark, iron, warm)
    make_landscape(stone, moss, grass, water)
    make_mill_support(stone, dark, iron)
    make_flume(wood, dark, water)
    return root, counts
