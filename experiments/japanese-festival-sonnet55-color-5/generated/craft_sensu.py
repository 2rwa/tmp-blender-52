"""Japanese folding sensu fan - fully opened, procedural mesh model for Blender 5.2."""

import bpy
import math
from mathutils import Vector

FAN_RIB_COUNT = 21
FAN_SPREAD_DEG = 160.0
RIB_LENGTH = 1.0
LEAF_INNER = 0.38
LEAF_OUTER = 0.96
PLEATS_PER_PANEL = 4


def make_material(name, color, roughness=0.6, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    rgba = (color[0], color[1], color[2], 1.0)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    bsdf = None
    for n in mat.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            bsdf = n
            break
    if bsdf is None:
        bsdf = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def make_object(name, verts, faces, materials, face_mats, collection):
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata([tuple(v) for v in verts], [], faces)
    mesh.update()
    for m in materials:
        mesh.materials.append(m)
    for i, p in enumerate(mesh.polygons):
        p.material_index = face_mats[i] if i < len(face_mats) else 0
        p.use_smooth = False
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def polar(r, ang, y=0.0):
    # fan lies in XZ plane, opening upward (+Z); ang measured from +Z axis
    return Vector((r * math.sin(ang), y, r * math.cos(ang)))


def box_between(verts, faces, fmats, p0, p1, p2, p3, thick_vec, mat_idx):
    """Add a thick quad slab (p0..p3 ccw) extruded by thick_vec."""
    base = len(verts)
    top = [p0, p1, p2, p3]
    bot = [p + thick_vec for p in top]
    verts.extend(top + bot)
    quads = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    for q in quads:
        faces.append([base + i for i in q])
        fmats.append(mat_idx)


def build_ribs(collection, mats):
    verts, faces, fmats = [], [], []
    n = FAN_RIB_COUNT
    half = math.radians(FAN_SPREAD_DEG) / 2.0
    for i in range(n):
        a = -half + (2 * half) * i / (n - 1)
        wr_in = 0.012
        wr_out = 0.030 if i not in (0, n - 1) else 0.045
        da_in = wr_in / 0.10
        da_out = wr_out / RIB_LENGTH
        r0 = 0.0
        y0 = -0.012 + (i % 2) * 0.004
        t = Vector((0, 0.008, 0))
        p0 = polar(0.05, a - da_in, y0)
        p1 = polar(0.05, a + da_in, y0)
        p2 = polar(RIB_LENGTH, a + da_out, y0)
        p3 = polar(RIB_LENGTH, a - da_out, y0)
        # make winding consistent
        box_between(verts, faces, fmats, p0, p3, p2, p1, t, 0 if i % 2 == 0 else 1)
    return make_object("BambooRibs", verts, faces, mats, fmats, collection)


def build_leaf(collection, mats):
    verts, faces, fmats = [], [], []
    n = FAN_RIB_COUNT - 1
    half = math.radians(FAN_SPREAD_DEG) / 2.0 - 0.01
    seg_ang = 2 * half / n
    sub = PLEATS_PER_PANEL
    # panel color pattern: indigo, ivory, scarlet repeating
    pattern = [2, 3, 4, 3]
    rings = [LEAF_INNER, 0.55, 0.72, LEAF_OUTER]
    ring_mats = [0, 1, 0]
    ring_cols = len(rings)
    total = n * sub
    cols = total + 1
    grid = []
    for c in range(cols):
        a = -half + 2 * half * c / total
        zig = 0.012 if c % 2 == 0 else -0.012
        col = []
        for r in rings:
            rr = r
            if r == LEAF_OUTER:
                rr = r + 0.015 * math.sin(a * 6)
            col.append(len(verts))
            verts.append(polar(rr, a, zig))
        grid.append(col)
    for c in range(total):
        panel = c // sub
        for k in range(ring_cols - 1):
            if k == 1:
                m = pattern[panel % len(pattern)]
                if (c % 2) == 1 and m == 3:
                    m = 3
            else:
                m = 2 if panel % 2 == 0 else 4
                if k == 0:
                    m = 2
                else:
                    m = 2 if panel % 2 == 0 else 4
            faces.append([grid[c][k], grid[c + 1][k], grid[c + 1][k + 1], grid[c][k + 1]])
            fmats.append(m)
            # reverse back face for visible thickness
    # back faces (slightly offset) for double-sided look
    base = len(verts)
    off = Vector((0, 0.004, 0))
    for c in range(cols):
        for k in range(ring_cols):
            verts.append(verts[grid[c][k]] + off)
    for c in range(total):
        for k in range(ring_cols - 1):
            i0 = base + c * ring_cols + k
            i1 = base + (c + 1) * ring_cols + k
            faces.append([i0, i0 + 1, i1 + 1, i1])
            fmats.append(3)
    # outer and inner edge strips
    for k in (0, ring_cols - 1):
        for c in range(total):
            a0 = grid[c][k]
            a1 = grid[c + 1][k]
            b0 = base + c * ring_cols + k
            b1 = base + (c + 1) * ring_cols + k
            faces.append([a0, a1, b1, b0])
            fmats.append(5)
    for c in (0, total):
        for k in range(ring_cols - 1):
            a0 = grid[c][k]
            a1 = grid[c][k + 1]
            b0 = base + c * ring_cols + k
            b1 = base + c * ring_cols + k + 1
            faces.append([a0, a1, b1, b0])
            fmats.append(5)
    return make_object("PleatedLeaf", verts, faces, mats, fmats, collection)


def build_edge_trim(collection, mats):
    verts, faces, fmats = [], [], []
    half = math.radians(FAN_SPREAD_DEG) / 2.0
    steps = 48
    for s in range(steps):
        a0 = -half + 2 * half * s / steps
        a1 = -half + 2 * half * (s + 1) / steps
        t = Vector((0, 0.010, 0))
        r_in, r_out = LEAF_OUTER - 0.012, LEAF_OUTER + 0.018
        box_between(verts, faces, fmats,
                    polar(r_in, a0, -0.008), polar(r_in, a1, -0.008),
                    polar(r_out, a1, -0.008), polar(r_out, a0, -0.008), t, 0)
        r_in, r_out = LEAF_INNER - 0.015, LEAF_INNER + 0.010
        box_between(verts, faces, fmats,
                    polar(r_in, a0, -0.008), polar(r_in, a1, -0.008),
                    polar(r_out, a1, -0.008), polar(r_out, a0, -0.008), t, 0)
    return make_object("DarkEdgeTrim", verts, faces, mats, fmats, collection)


def build_rivet(collection, mats):
    verts, faces, fmats = [], [], []
    seg = 16
    for (y0, y1, rad) in ((-0.03, 0.03, 0.022), (-0.034, -0.028, 0.038), (0.026, 0.032, 0.038)):
        base = len(verts)
        for j in range(seg):
            ang = 2 * math.pi * j / seg
            x, z = rad * math.cos(ang), rad * math.sin(ang)
            verts.append((x, y0, z))
            verts.append((x, y1, z))
        for j in range(seg):
            a = base + 2 * j
            b = base + 2 * ((j + 1) % seg)
            faces.append([a, b, b + 1, a + 1])
            fmats.append(0)
        faces.append([base + 2 * j for j in reversed(range(seg))])
        fmats.append(0)
        faces.append([base + 2 * j + 1 for j in range(seg)])
        fmats.append(0)
    return make_object("PivotRivet", verts, faces, mats, fmats, collection)


def build_tassel(collection, mats):
    verts, faces, fmats = [], [], []
    # small cord loop and tassel at the pivot base
    base_pt = Vector((0, -0.04, -0.02))
    pts = [base_pt, base_pt + Vector((0, -0.01, -0.12)), base_pt + Vector((0.01, -0.01, -0.25))]
    for i in range(len(pts) - 1):
        p, q = pts[i], pts[i + 1]
        w = 0.008
        box_between(verts, faces, fmats, p + Vector((-w, 0, 0)), p + Vector((w, 0, 0)),
                    q + Vector((w, 0, 0)), q + Vector((-w, 0, 0)), Vector((0, -0.01, 0)), 0)
    tip = pts[-1]
    for k in range(5):
        x = (k - 2) * 0.012
        box_between(verts, faces, fmats, tip + Vector((x - 0.005, 0, 0)), tip + Vector((x + 0.005, 0, 0)),
                    tip + Vector((x + 0.005, 0, -0.14)), tip + Vector((x - 0.005, 0, -0.14)),
                    Vector((0, -0.01, 0)), 1)
    return make_object("ScarletTassel", verts, faces, mats, fmats, collection)


def build_model():
    collection = bpy.context.scene.collection
    bamboo = make_material("BambooTan", (0.78, 0.55, 0.25), 0.5)
    bamboo_dark = make_material("BambooAmber", (0.55, 0.32, 0.12), 0.5)
    indigo = make_material("IndigoBlue", (0.05, 0.12, 0.45), 0.7)
    ivory = make_material("IvoryPaper", (0.97, 0.92, 0.78), 0.8)
    scarlet = make_material("ScarletRed", (0.85, 0.07, 0.06), 0.7)
    dark = make_material("DarkLacquer", (0.04, 0.03, 0.03), 0.4)
    gold = make_material("GoldRivet", (0.9, 0.7, 0.15), 0.3, 0.8)

    rib_mats = [bamboo, bamboo_dark]
    leaf_mats = [bamboo, bamboo_dark, indigo, ivory, scarlet, dark]
    build_ribs(collection, rib_mats)
    build_leaf(collection, leaf_mats)
    build_edge_trim(collection, [dark])
    build_rivet(collection, [gold])
    build_tassel(collection, [scarlet, ivory])
    return None
