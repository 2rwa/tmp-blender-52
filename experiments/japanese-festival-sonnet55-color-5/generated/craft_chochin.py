"""Japanese chochin festival lantern: procedural model for Blender 5.2.2."""
import bpy
import math
from mathutils import Vector


def make_material(name, color):
    mat = bpy.data.materials.new(name=name)
    rgba = (color[0], color[1], color[2], 1.0)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        for n in mat.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                bsdf = n
                break
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = rgba
    return mat


def make_object(name, verts, faces, mat, collection):
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    for p in mesh.polygons:
        p.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def profile_radius(t, r_max, r_end):
    """t in 0..1 from bottom to top; bulging chochin silhouette."""
    s = math.sin(math.pi * t)
    return r_end + (r_max - r_end) * (s ** 0.6)


def lathe(profile, segs, a0=0.0, a1=2 * math.pi, closed=True):
    """profile: list of (r, z). Returns verts, faces."""
    verts = []
    faces = []
    n = len(profile)
    cols = segs if closed else segs + 1
    for (r, z) in profile:
        for i in range(cols):
            a = a0 + (a1 - a0) * i / segs
            verts.append((r * math.cos(a), r * math.sin(a), z))
    span = segs if closed else segs
    for j in range(n - 1):
        for i in range(span):
            i2 = (i + 1) % cols
            faces.append((j * cols + i, j * cols + i2,
                          (j + 1) * cols + i2, (j + 1) * cols + i))
    return verts, faces


def add_torus(name, major, minor, z, mat, collection, ms=32, mn=8):
    verts = []
    faces = []
    for i in range(ms):
        a = 2 * math.pi * i / ms
        for j in range(mn):
            b = 2 * math.pi * j / mn
            r = major + minor * math.cos(b)
            verts.append((r * math.cos(a), r * math.sin(a), z + minor * math.sin(b)))
    for i in range(ms):
        for j in range(mn):
            i2 = (i + 1) % ms
            j2 = (j + 1) % mn
            faces.append((i * mn + j, i2 * mn + j, i2 * mn + j2, i * mn + j2))
    return make_object(name, verts, faces, mat, collection)


def add_cylinder(name, r, z0, z1, mat, collection, segs=24, cx=0.0, cy=0.0, r1=None):
    r1 = r if r1 is None else r1
    verts = []
    for i in range(segs):
        a = 2 * math.pi * i / segs
        verts.append((cx + r * math.cos(a), cy + r * math.sin(a), z0))
    for i in range(segs):
        a = 2 * math.pi * i / segs
        verts.append((cx + r1 * math.cos(a), cy + r1 * math.sin(a), z1))
    faces = []
    for i in range(segs):
        i2 = (i + 1) % segs
        faces.append((i, i2, segs + i2, segs + i))
    faces.append(tuple(reversed(range(segs))))
    faces.append(tuple(range(segs, 2 * segs)))
    return make_object(name, verts, faces, mat, collection)


def build_model():
    col = bpy.context.collection
    paper = make_material("Paper_WarmWhite", (1.0, 0.93, 0.70))
    red = make_material("Panel_Red", (0.85, 0.03, 0.03))
    black = make_material("Lacquer_Black", (0.02, 0.02, 0.025))
    gold = make_material("Gold_Accent", (0.95, 0.70, 0.08))
    cord = make_material("Cord_Crimson", (0.6, 0.0, 0.08))

    H = 1.6
    z_bot = 0.35
    r_max = 0.55
    r_end = 0.36
    segs = 48
    rings = 20

    def zt(t):
        return z_bot + H * t

    # Paper body (thin double-shelled: outer and slightly inner)
    prof = []
    for k in range(rings + 1):
        t = k / rings
        prof.append((profile_radius(t, r_max, r_end), zt(t)))
    v, f = lathe(prof, segs)
    make_object("Paper_Body", v, f, paper, col)
    prof_in = [(r - 0.015, z) for (r, z) in prof]
    v, f = lathe(prof_in, segs)
    f = [tuple(reversed(x)) for x in f]
    make_object("Paper_Inner", v, f, paper, col)

    # Red bands: slightly raised strips on body at top and bottom
    for nm, t0, t1 in (("Red_Band_Top", 0.80, 0.90), ("Red_Band_Bottom", 0.10, 0.20)):
        pr = []
        m = 4
        for k in range(m + 1):
            t = t0 + (t1 - t0) * k / m
            pr.append((profile_radius(t, r_max, r_end) + 0.008, zt(t)))
        v, f = lathe(pr, segs)
        make_object(nm, v, f, red, col)

    # Central red panel zone (broad band) with geometric ornament
    pr = []
    m = 6
    for k in range(m + 1):
        t = 0.30 + 0.40 * k / m
        pr.append((profile_radius(t, r_max, r_end) + 0.006, zt(t)))
    # Two opposite red panels (front/back), arc spans of 70 degrees
    for idx, center in enumerate((math.pi / 2, 3 * math.pi / 2)):
        half = math.radians(36)
        v, f = lathe(pr, 8, a0=center - half, a1=center + half, closed=False)
        make_object("Red_Panel_%d" % idx, v, f, red, col)

        # Lettering-like geometric ornament: black bars & diamonds on panel
        for bi, (t, w, h) in enumerate(((0.62, 0.34, 0.025), (0.38, 0.34, 0.025),
                                        (0.50, 0.05, 0.16))):
            z = zt(t)
            r = profile_radius(t, r_max, r_end) + 0.014
            hw = w / 2
            hh = h / 2 + 0.0
            dirv = Vector((math.cos(center), math.sin(center), 0))
            tang = Vector((-math.sin(center), math.cos(center), 0))
            c = dirv * r + Vector((0, 0, z))
            pts = [c - tang * hw - Vector((0, 0, hh)), c + tang * hw - Vector((0, 0, hh)),
                   c + tang * hw + Vector((0, 0, hh)), c - tang * hw + Vector((0, 0, hh))]
            vv = [tuple(p) for p in pts]
            # pull slightly forward
            make_object("Ornament_Bar_%d_%d" % (idx, bi), vv, [(0, 1, 2, 3)], black, col)
        # diamond
        t = 0.50
        z = zt(t)
        r = profile_radius(t, r_max, r_end) + 0.016
        dirv = Vector((math.cos(center), math.sin(center), 0))
        tang = Vector((-math.sin(center), math.cos(center), 0))
        c = dirv * r + Vector((0, 0, z))
        d = 0.09
        vv = [tuple(c - tang * d), tuple(c - Vector((0, 0, d))),
              tuple(c + tang * d), tuple(c + Vector((0, 0, d)))]
        make_object("Ornament_Diamond_%d" % idx, vv, [(0, 1, 2, 3)], gold, col)

    # Ribs: thin black meridian strips that follow profile
    n_ribs = 24
    rib_w = 0.012
    for ri in range(n_ribs):
        a = 2 * math.pi * ri / n_ribs
        verts = []
        faces = []
        steps = 24
        for k in range(steps + 1):
            t = k / steps
            r = profile_radius(t, r_max, r_end) + 0.012
            z = zt(t)
            for s in (-1, 1):
                aa = a + s * rib_w / r
                verts.append((r * math.cos(aa), r * math.sin(aa), z))
        for k in range(steps):
            b = k * 2
            faces.append((b, b + 1, b + 3, b + 2))
        make_object("Rib_%02d" % ri, verts, faces, black, col)

    # Black lacquered caps (top and bottom rims)
    z_top = zt(1.0)
    for nm, zc, sign in (("Rim_Top", z_top, 1), ("Rim_Bottom", z_bot, -1)):
        h = 0.11
        z0, z1 = (zc - 0.02, zc + h) if sign == 1 else (zc - h, zc + 0.02)
        add_cylinder(nm, r_end + 0.03, z0, z1, black, col, segs=48)
        add_torus(nm + "_Ring", r_end + 0.03, 0.022, zc + sign * h, black, col, ms=48)
        add_torus(nm + "_Gold", r_end + 0.035, 0.012, zc + sign * (h * 0.5), gold, col, ms=48, mn=6)

    # Upper loop (hanging handle)
    loop_z = z_top + 0.11
    add_cylinder("Loop_Post", 0.03, loop_z, loop_z + 0.08, black, col, segs=12)
    verts = []
    faces = []
    ms, mn = 20, 8
    cz = loop_z + 0.22
    for i in range(ms):
        a = 2 * math.pi * i / ms
        cx = 0.12 * math.cos(a)
        cz2 = cz + 0.14 * math.sin(a)
        for j in range(mn):
            b = 2 * math.pi * j / mn
            rr = 0.015 * math.cos(b)
            verts.append((cx + rr * 0.0, 0.015 * math.sin(b), cz2 + rr))
    for i in range(ms):
        for j in range(mn):
            i2 = (i + 1) % ms
            j2 = (j + 1) % mn
            faces.append((i * mn + j, i2 * mn + j, i2 * mn + j2, i * mn + j2))
    make_object("Upper_Loop", verts, faces, cord, col)
    # Fix loop: it is built in XZ plane; centered at x=0 offset
    # (cx is already around origin)

    # Bottom tassel
    tz = z_bot - 0.11
    add_cylinder("Tassel_Cap", 0.05, tz - 0.08, tz, gold, col, segs=16, r1=0.035)
    add_cylinder("Tassel_Knot", 0.045, tz - 0.16, tz - 0.08, red, col, segs=16, r1=0.05)
    n_str = 28
    for i in range(n_str):
        a = 2 * math.pi * i / n_str
        rr = 0.04 * (0.4 + 0.6 * (i % 2))
        top = (rr * math.cos(a) * 0.6, rr * math.sin(a) * 0.6, tz - 0.16)
        bot = (rr * math.cos(a) * 1.6, rr * math.sin(a) * 1.6, tz - 0.62)
        w = 0.008
        tx, ty = -math.sin(a) * w, math.cos(a) * w
        vv = [(top[0] - tx, top[1] - ty, top[2]), (top[0] + tx, top[1] + ty, top[2]),
              (bot[0] + tx, bot[1] + ty, bot[2]), (bot[0] - tx, bot[1] - ty, bot[2])]
        make_object("Tassel_Strand_%02d" % i, vv, [(0, 1, 2, 3)], cord if i % 2 else red, col)

    # Internal candle holder disc (visible through paper)
    add_cylinder("Inner_Base", 0.2, z_bot + 0.03, z_bot + 0.05, black, col, segs=24)
    add_cylinder("Inner_Candle", 0.03, z_bot + 0.05, z_bot + 0.3, gold, col, segs=12)
