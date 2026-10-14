"""Japanese wagasa umbrella: procedural Blender 5.2 model."""
import bpy
import math
import mathutils


def make_material(name, color):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    rgba = (color[0], color[1], color[2], 1.0)
    mat.diffuse_color = rgba
    bsdf = None
    if mat.node_tree:
        for n in mat.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                bsdf = n
                break
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = rgba
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


def add_tube(verts, faces, p0, p1, r0, r1, seg=6, cap=True):
    """Append a tapered tube between two points."""
    a = mathutils.Vector(p0)
    b = mathutils.Vector(p1)
    d = (b - a).normalized()
    up = mathutils.Vector((0, 0, 1))
    if abs(d.dot(up)) > 0.95:
        up = mathutils.Vector((1, 0, 0))
    u = d.cross(up).normalized()
    v = d.cross(u).normalized()
    base = len(verts)
    for c, r in ((a, r0), (b, r1)):
        for i in range(seg):
            t = 2 * math.pi * i / seg
            verts.append(tuple(c + u * math.cos(t) * r + v * math.sin(t) * r))
    for i in range(seg):
        j = (i + 1) % seg
        faces.append((base + i, base + j, base + seg + j, base + seg + i))
    if cap:
        faces.append(tuple(base + i for i in reversed(range(seg))))
        faces.append(tuple(base + seg + i for i in range(seg)))


def add_ring(verts, faces, z, radius, tube_r, major=32, minor=6):
    """Append a torus-like ring (binding) at height z."""
    base = len(verts)
    for i in range(major):
        a = 2 * math.pi * i / major
        for j in range(minor):
            t = 2 * math.pi * j / minor
            rr = radius + tube_r * math.cos(t)
            verts.append((rr * math.cos(a), rr * math.sin(a), z + tube_r * math.sin(t)))
    for i in range(major):
        i2 = (i + 1) % major
        for j in range(minor):
            j2 = (j + 1) % minor
            faces.append((base + i * minor + j, base + i2 * minor + j,
                          base + i2 * minor + j2, base + i * minor + j2))


def canopy_profile(r):
    """Height of canopy at radial fraction r (0 center .. 1 rim)."""
    return 1.15 - 0.62 * (r ** 2) - 0.05 * r


def build_model():
    col = bpy.context.scene.collection
    crimson = make_material("Crimson_Paper", (0.82, 0.03, 0.07))
    cream = make_material("Cream_Paper", (0.97, 0.90, 0.68))
    gold = make_material("Gold_Ornament", (1.0, 0.70, 0.08))
    bamboo = make_material("Bamboo_Rib", (0.72, 0.52, 0.22))
    wood = make_material("Handle_Wood", (0.38, 0.16, 0.06))
    thread = make_material("Binding_Thread", (0.05, 0.05, 0.07))
    dark = make_material("Dark_Lacquer", (0.12, 0.02, 0.02))

    ribs_n = 32
    rings = 14
    R = 1.0
    thick = 0.006
    ang_step = 2 * math.pi / ribs_n

    # Canopy: alternating crimson / cream segment bands, double-sided shell
    # Radially divide: inner cream disc zone, crimson main, cream rim band
    crim_v, crim_f = [], []
    cream_v, cream_f = [], []
    gold_v, gold_f = [], []
    sub = 2  # angular subdivisions per rib gap
    nang = ribs_n * sub
    rad_levels = [0.0] + [0.09 + (1 - 0.09) * k / (rings - 1) for k in range(rings)]
    rad_levels = [0.0] + [0.1 + 0.9 * k / (rings - 1) for k in range(rings)]

    def pt(r, a, off):
        h = canopy_profile(r) + off
        return (R * r * math.cos(a), R * r * math.sin(a), h)

    # Build one vertex grid for top and bottom surfaces
    def grid(vl, fl, rmin_i, rmax_i):
        top = {}
        bot = {}
        for ri in range(rmin_i, rmax_i + 1):
            r = rad_levels[ri]
            for ai in range(nang):
                a = ai * 2 * math.pi / nang
                top[(ri, ai)] = len(vl)
                vl.append(pt(r, a, thick))
        for ri in range(rmin_i, rmax_i + 1):
            r = rad_levels[ri]
            for ai in range(nang):
                a = ai * 2 * math.pi / nang
                bot[(ri, ai)] = len(vl)
                vl.append(pt(r, a, -thick))
        for ri in range(rmin_i, rmax_i):
            for ai in range(nang):
                a2 = (ai + 1) % nang
                fl.append((top[(ri, ai)], top[(ri, a2)], top[(ri + 1, a2)], top[(ri + 1, ai)]))
                fl.append((bot[(ri, ai)], bot[(ri + 1, ai)], bot[(ri + 1, a2)], bot[(ri, a2)]))
        for ai in range(nang):
            a2 = (ai + 1) % nang
            fl.append((top[(rmax_i, ai)], top[(rmax_i, a2)], bot[(rmax_i, a2)], bot[(rmax_i, ai)]))

    # Zones: cream center 0..2, crimson 2..11, cream rim 11..14
    n = len(rad_levels) - 1
    grid(cream_v, cream_f, 0, 2)
    grid(crim_v, crim_f, 2, 11)
    grid(cream_v, cream_f, 11, n)
    # (second/third grids share a vertex list; indices offset correctly because appended)
    make_object("Canopy_Crimson_Paper", crim_v, crim_f, crimson, col)
    make_object("Canopy_Cream_Paper", cream_v, cream_f, cream, col)

    # Gold ornament rings on canopy surface
    for ri, w in ((2, 0.012), (11, 0.012)):
        r = rad_levels[ri]
        base = len(gold_v)
        for ai in range(nang):
            a = ai * 2 * math.pi / nang
            for dr in (-w, w):
                rr = r + dr
                gold_v.append(pt(rr, a, thick + 0.004))
        for ai in range(nang):
            a2 = (ai + 1) % nang
            gold_f.append((base + ai * 2, base + a2 * 2, base + a2 * 2 + 1, base + ai * 2 + 1))
    # Gold petal-like diamonds between ribs
    for k in range(ribs_n):
        a = (k + 0.5) * ang_step
        c_r = 0.68
        pts = [(c_r - 0.07, 0.0), (c_r, 0.025), (c_r + 0.07, 0.0), (c_r, -0.025)]
        base = len(gold_v)
        for rr, da in pts:
            aa = a + da / max(rr, 0.1) * 1.0
            gold_v.append(pt(rr, aa, thick + 0.005))
        gold_f.append((base, base + 1, base + 2, base + 3))
    # Gold outer rim trim
    base = len(gold_v)
    for ai in range(nang):
        a = ai * 2 * math.pi / nang
        gold_v.append(pt(0.995, a, thick + 0.004))
        gold_v.append(pt(1.0, a, thick + 0.004))
    for ai in range(nang):
        a2 = (ai + 1) % nang
        gold_f.append((base + ai * 2, base + a2 * 2, base + a2 * 2 + 1, base + ai * 2 + 1))
    make_object("Gold_Ornaments", gold_v, gold_f, gold, col)

    # Bamboo ribs beneath canopy, plus inner struts to the runner
    rib_v, rib_f = [], []
    strut_v, strut_f = [], []
    spokes_samples = 10
    runner_z = 0.55
    for k in range(ribs_n):
        a = k * ang_step
        ca, sa = math.cos(a), math.sin(a)
        prev = None
        for s in range(spokes_samples + 1):
            r = 0.04 + 0.95 * s / spokes_samples
            p = (R * r * ca, R * r * sa, canopy_profile(r) - 0.025)
            if prev is not None:
                add_tube(rib_v, rib_f, prev[0], p, prev[1], 0.009 - 0.004 * (s / spokes_samples), seg=4, cap=False)
            prev = (p, 0.009 - 0.004 * (s / spokes_samples))
        # strut from mid rib to runner on shaft
        r_mid = 0.5
        p_mid = (R * r_mid * ca, R * r_mid * sa, canopy_profile(r_mid) - 0.03)
        p_run = (0.07 * ca, 0.07 * sa, runner_z)
        add_tube(strut_v, strut_f, p_mid, p_run, 0.006, 0.006, seg=4)
    make_object("Bamboo_Ribs", rib_v, rib_f, bamboo, col)
    make_object("Bamboo_Struts", strut_v, strut_f, bamboo, col)

    # Rim cross threads (bindings between ribs) at three radii
    th_v, th_f = [], []
    for r in (0.35, 0.6, 0.85):
        for k in range(ribs_n):
            a0 = k * ang_step
            a1 = (k + 1) * ang_step
            p0 = (R * r * math.cos(a0), R * r * math.sin(a0), canopy_profile(r) - 0.04)
            p1 = (R * r * math.cos(a1), R * r * math.sin(a1), canopy_profile(r) - 0.04)
            add_tube(th_v, th_f, p0, p1, 0.0035, 0.0035, seg=4, cap=False)
    # Neat bindings at the rib ends
    for k in range(ribs_n):
        a = k * ang_step
        p0 = (0.985 * math.cos(a), 0.985 * math.sin(a), canopy_profile(0.985) - 0.03)
        p1 = (1.0 * math.cos(a), 1.0 * math.sin(a), canopy_profile(1.0) - 0.03)
        add_tube(th_v, th_f, p0, p1, 0.012, 0.012, seg=6)
    make_object("Thread_Bindings", th_v, th_f, thread, col)

    # Handle / shaft: carved wood with grip rings
    sh_v, sh_f = [], []
    add_tube(sh_v, sh_f, (0, 0, -0.75), (0, 0, 1.12), 0.028, 0.02, seg=12)
    # carved grip: stacked swollen segments
    for i in range(8):
        z0 = -0.75 + i * 0.06
        add_tube(sh_v, sh_f, (0, 0, z0), (0, 0, z0 + 0.05), 0.036 if i % 2 == 0 else 0.032,
                 0.042 if i % 2 == 0 else 0.036, seg=12)
    # pommel
    add_tube(sh_v, sh_f, (0, 0, -0.82), (0, 0, -0.74), 0.026, 0.042, seg=12)
    make_object("Handle_Carved_Wood", sh_v, sh_f, wood, col)

    # Dark lacquer runner / upper hub and lower stretcher disc
    hub_v, hub_f = [], []
    add_tube(hub_v, hub_f, (0, 0, 0.50), (0, 0, 0.62), 0.07, 0.06, seg=16)
    add_tube(hub_v, hub_f, (0, 0, 0.88), (0, 0, 0.96), 0.09, 0.05, seg=16)
    add_tube(hub_v, hub_f, (0, 0, -0.05), (0, 0, 0.02), 0.045, 0.045, seg=16)
    make_object("Lacquer_Hubs", hub_v, hub_f, dark, col)

    # Gold reinforced tip, ferrule, and bands
    g2_v, g2_f = [], []
    add_tube(g2_v, g2_f, (0, 0, 1.10), (0, 0, 1.22), 0.03, 0.012, seg=12)
    add_tube(g2_v, g2_f, (0, 0, 1.22), (0, 0, 1.28), 0.012, 0.0, seg=12, cap=False)
    add_tube(g2_v, g2_f, (0, 0, 1.04), (0, 0, 1.10), 0.07, 0.07, seg=20)
    add_tube(g2_v, g2_f, (0, 0, -0.60), (0, 0, -0.58), 0.046, 0.046, seg=12)
    add_tube(g2_v, g2_f, (0, 0, -0.30), (0, 0, -0.28), 0.04, 0.04, seg=12)
    make_object("Gold_Tip_And_Bands", g2_v, g2_f, gold, col)

    # Binding ring at the top paper opening
    rb_v, rb_f = [], []
    add_ring(rb_v, rb_f, 1.03, 0.09, 0.012, major=24, minor=6)
    make_object("Crimson_Top_Binding", rb_v, rb_f, crimson, col)
