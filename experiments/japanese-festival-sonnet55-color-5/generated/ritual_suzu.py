"""Kagura suzu: Japanese ritual bell wand with tiered golden bells, red lacquered grip and ribbons."""
import bpy
import math
from mathutils import Vector


def make_material(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    rgba = (color[0], color[1], color[2], 1.0)
    mat.diffuse_color = rgba
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = rgba
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
    mat.metallic = metallic
    mat.roughness = roughness
    return mat


def make_object(name, verts, faces, mat, collection, smooth=True):
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    if smooth:
        for p in mesh.polygons:
            p.use_smooth = True
    return obj


def lathe(profile, segments, center=(0.0, 0.0, 0.0), closed_top=False, closed_bottom=False):
    """Revolve (radius, z) profile around Z axis."""
    cx, cy, cz = center
    verts = []
    faces = []
    n = len(profile)
    for r, z in profile:
        for i in range(segments):
            a = 2 * math.pi * i / segments
            verts.append((cx + r * math.cos(a), cy + r * math.sin(a), cz + z))
    for j in range(n - 1):
        for i in range(segments):
            i2 = (i + 1) % segments
            faces.append((j * segments + i, j * segments + i2,
                          (j + 1) * segments + i2, (j + 1) * segments + i))
    if closed_bottom:
        faces.append(tuple(reversed(range(segments))))
    if closed_top:
        faces.append(tuple(range((n - 1) * segments, n * segments)))
    return verts, faces


def tube(points, radius, sides, ):
    """Tube along a polyline with capped ends."""
    verts = []
    faces = []
    pts = [Vector(p) for p in points]
    m = len(pts)
    for k in range(m):
        if k == 0:
            t = pts[1] - pts[0]
        elif k == m - 1:
            t = pts[-1] - pts[-2]
        else:
            t = pts[k + 1] - pts[k - 1]
        t.normalize()
        ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        u = t.cross(ref).normalized()
        v = t.cross(u).normalized()
        for i in range(sides):
            a = 2 * math.pi * i / sides
            verts.append(tuple(pts[k] + u * math.cos(a) * radius + v * math.sin(a) * radius))
    for k in range(m - 1):
        for i in range(sides):
            i2 = (i + 1) % sides
            faces.append((k * sides + i, k * sides + i2, (k + 1) * sides + i2, (k + 1) * sides + i))
    faces.append(tuple(reversed(range(sides))))
    faces.append(tuple(range((m - 1) * sides, m * sides)))
    return verts, faces


def bell_geometry(radius, seg=14):
    """Spherical suzu bell: two-hemisphere body with equatorial band, slit and loop."""
    profile = []
    # bottom pole to top pole
    steps = 8
    for k in range(steps + 1):
        phi = -math.pi / 2 + math.pi * k / steps
        r = radius * math.cos(phi)
        z = radius * math.sin(phi)
        if k == 0:
            r = 0.001 * radius
        if k == steps:
            r = 0.001 * radius
        profile.append((r, z))
    return lathe(profile, seg)


def add_bell(name, pos, radius, gold, dark, collection, parts):
    x, y, z = pos
    v, f = bell_geometry(radius)
    v = [(a + x, b + y, c + z) for a, b, c in v]
    parts.append(make_object(name + "_Body", v, f, gold, collection))
    # equator band (slightly larger ring)
    prof = [(radius * 1.03, -radius * 0.07), (radius * 1.06, -radius * 0.03),
            (radius * 1.06, radius * 0.03), (radius * 1.03, radius * 0.07)]
    v, f = lathe(prof, 14, center=(x, y, z))
    parts.append(make_object(name + "_Band", v, f, gold, collection))
    # dark slit at the bottom
    prof = [(radius * 0.02, -radius * 0.99), (radius * 0.30, -radius * 0.93),
            (radius * 0.30, -radius * 0.90), (radius * 0.02, -radius * 0.96)]
    v, f = lathe(prof, 10, center=(x, y, z))
    parts.append(make_object(name + "_Slit", v, f, dark, collection))
    # top loop ring (torus-like)
    loop = []
    for k in range(8):
        a = 2 * math.pi * k / 8
        loop.append((x + radius * 0.0, y + radius * 0.22 * math.cos(a) * 0.0,
                     z + radius * 1.12 + radius * 0.2 * math.sin(a)))
    pts = [(x + radius * 0.22 * math.cos(2 * math.pi * k / 8), y,
            z + radius * 1.1 + radius * 0.22 * math.sin(2 * math.pi * k / 8)) for k in range(9)]
    v, f = tube(pts, radius * 0.07, 5)
    parts.append(make_object(name + "_Loop", v, f, gold, collection))


def build_model():
    col = bpy.context.scene.collection
    gold = make_material("Yellow_Gold", (1.0, 0.72, 0.08), 1.0, 0.25)
    dark_gold = make_material("Dark_Gold_Slit", (0.35, 0.2, 0.02), 0.5, 0.5)
    red = make_material("Red_Lacquer", (0.75, 0.04, 0.03), 0.1, 0.2)
    ivory = make_material("Ivory_Wrap", (0.97, 0.93, 0.78), 0.0, 0.6)
    black = make_material("Black_Lacquer", (0.03, 0.02, 0.02), 0.2, 0.3)
    ribbon_mats = [
        make_material("Ribbon_Red", (0.9, 0.05, 0.1)),
        make_material("Ribbon_White", (0.98, 0.98, 0.98)),
        make_material("Ribbon_Blue", (0.1, 0.25, 0.85)),
        make_material("Ribbon_Green", (0.1, 0.65, 0.25)),
        make_material("Ribbon_Purple", (0.55, 0.15, 0.7)),
    ]
    parts = []

    # Grip (red lacquered wood), z from 0 to 0.9
    prof = [(0.001, 0.0), (0.028, 0.0), (0.034, 0.03), (0.030, 0.08), (0.026, 0.3),
            (0.028, 0.6), (0.030, 0.82), (0.036, 0.88), (0.030, 0.92), (0.001, 0.92)]
    v, f = lathe(prof, 16)
    parts.append(make_object("Grip_RedLacquer", v, f, red, col))

    # Pommel cap
    prof = [(0.001, -0.05), (0.02, -0.045), (0.036, -0.01), (0.038, 0.01), (0.034, 0.03), (0.001, 0.03)]
    v, f = lathe(prof, 16)
    parts.append(make_object("Grip_Pommel", v, f, gold, col))

    # Wrap: alternating ivory rings with red diagonal feel (ivory bands)
    for i in range(9):
        z0 = 0.14 + i * 0.075
        prof = [(0.0300, z0), (0.0335, z0 + 0.006), (0.0335, z0 + 0.044), (0.0300, z0 + 0.050)]
        v, f = lathe(prof, 16)
        parts.append(make_object("Grip_IvoryWrap_%d" % i, v, f, ivory, col))
        # red cord between
        prof = [(0.030, z0 + 0.050), (0.0345, z0 + 0.054), (0.0345, z0 + 0.071), (0.030, z0 + 0.075)]
        v, f = lathe(prof, 16)
        parts.append(make_object("Grip_RedCord_%d" % i, v, f, red, col))

    # Collar and golden hub
    prof = [(0.03, 0.92), (0.05, 0.93), (0.055, 0.96), (0.04, 0.99), (0.03, 1.0)]
    v, f = lathe(prof, 16)
    parts.append(make_object("Collar_Gold", v, f, gold, col))
    prof = [(0.03, 1.0), (0.045, 1.02), (0.05, 1.06), (0.04, 1.09), (0.001, 1.09)]
    v, f = lathe(prof, 16)
    parts.append(make_object("Hub_Black", v, f, black, col))

    # Central shaft
    v, f = tube([(0, 0, 1.05), (0, 0, 1.30), (0, 0, 1.46)], 0.012, 8)
    parts.append(make_object("Central_Shaft", v, f, gold, col))

    # Branches: three tiers, outward-spreading
    tiers = [(1.10, 6, 0.30, 0.65, 0.050), (1.22, 5, 0.22, 0.60, 0.045), (1.34, 4, 0.14, 0.52, 0.040)]
    bell_count = 0
    rib_count = 0
    for ti, (zb, nb, reach, lift, br) in enumerate(tiers):
        for b in range(nb):
            a = 2 * math.pi * b / nb + ti * math.pi / nb
            dx, dy = math.cos(a), math.sin(a)
            p0 = (dx * 0.03, dy * 0.03, zb)
            p1 = (dx * reach * 0.6, dy * reach * 0.6, zb + 0.06 + lift * 0.1)
            p2 = (dx * reach, dy * reach, zb + 0.08 + lift * 0.25)
            v, f = tube([p0, p1, p2], 0.008, 6)
            parts.append(make_object("Branch_%d_%d" % (ti, b), v, f, gold, col))
            # bell cluster at branch tip: hanging bell below plus small bells
            r = br * 0.8
            add_bell("Bell_%d_%d_main" % (ti, b), (p2[0], p2[1], p2[2] + r * 1.3),
                     r, gold, dark_gold, col, parts)
            bell_count += 1
            # tiny bells around
            for s in range(2):
                sa = a + (s * 2 - 1) * 0.35
                sx = p1[0] + math.cos(sa) * 0.0
                add_bell("Bell_%d_%d_small%d" % (ti, b, s),
                         (p1[0] + (-dy) * (s * 2 - 1) * 0.04, p1[1] + dx * (s * 2 - 1) * 0.04, p1[2] - 0.05),
                         r * 0.55, gold, dark_gold, col, parts)
            # hanging ribbon from main bell
            rm = ribbon_mats[(rib_count) % len(ribbon_mats)]
            rib_count += 1
            bx, by, bz = p2[0], p2[1], p2[2] + r * 1.3 - r
            w = 0.012
            L = 0.28 + 0.04 * (b % 3)
            sway = 0.02
            vs = [(bx - dy * w, by + dx * w, bz), (bx + dy * w, by - dx * w, bz),
                  (bx + dy * w + dx * sway, by - dx * w + dy * sway, bz - L),
                  (bx - dy * w + dx * sway, by + dx * w + dy * sway, bz - L)]
            fs = [(0, 1, 2, 3), (3, 2, 1, 0)]
            parts.append(make_object("Ribbon_%d_%d" % (ti, b), vs, fs, rm, col, smooth=False))

    # Top finial: crowning large bell and flame jewel
    add_bell("Bell_Crown", (0, 0, 1.46 + 0.05), 0.05, gold, dark_gold, col, parts)
    prof = [(0.001, 1.62), (0.012, 1.64), (0.015, 1.67), (0.008, 1.71), (0.001, 1.75)]
    v, f = lathe(prof, 10)
    parts.append(make_object("Finial_Jewel", v, f, red, col))

    # Central ribbons tied at hub
    for k in range(5):
        a = 2 * math.pi * k / 5
        dx, dy = math.cos(a), math.sin(a)
        bx, by, bz = dx * 0.045, dy * 0.045, 1.04
        w = 0.014
        L = 0.45 + 0.05 * k
        vs = [(bx - dy * w, by + dx * w, bz), (bx + dy * w, by - dx * w, bz),
              (bx + dy * w + dx * 0.05, by - dx * w + dy * 0.05, bz - L),
              (bx - dy * w + dx * 0.05, by + dx * w + dy * 0.05, bz - L)]
        parts.append(make_object("Hub_Ribbon_%d" % k, vs, [(0, 1, 2, 3), (3, 2, 1, 0)],
                                 ribbon_mats[k % len(ribbon_mats)], col, smooth=False))

    # Center grip in world: shift so model sits around origin
    for o in parts:
        o.location.z -= 0.55
    return parts
