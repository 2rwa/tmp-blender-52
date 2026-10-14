"""Japanese tsuzumi hand drum - procedural Blender 5.2 model."""
import bpy
import math
from mathutils import Vector


def make_material(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    rgba = (color[0], color[1], color[2], 1.0)
    mat.diffuse_color = rgba
    bsdf = None
    for n in mat.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            bsdf = n
            break
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = rgba
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
    return mat


def make_object(name, verts, faces, mat, smooth=True):
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata([tuple(v) for v in verts], [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    if smooth:
        for p in mesh.polygons:
            p.use_smooth = True
    return obj


def body_radius(z, h, r_end, r_waist):
    """Hourglass profile, z in [-h, h]."""
    t = abs(z) / h
    # smooth curve: waist at t=0, flare near end
    s = t ** 1.8
    return r_waist + (r_end - r_waist) * s


def lathe(name, profile, mat, seg=32, close_ends=False):
    """profile: list of (r, z). Builds surface of revolution."""
    verts = []
    faces = []
    n = len(profile)
    for (r, z) in profile:
        for i in range(seg):
            a = 2 * math.pi * i / seg
            verts.append((r * math.cos(a), r * math.sin(a), z))
    for j in range(n - 1):
        for i in range(seg):
            i2 = (i + 1) % seg
            faces.append([j * seg + i, j * seg + i2, (j + 1) * seg + i2, (j + 1) * seg + i])
    if close_ends:
        for j, rev in ((0, True), (n - 1, False)):
            if profile[j][0] > 1e-6:
                c = len(verts)
                verts.append((0, 0, profile[j][1]))
                for i in range(seg):
                    i2 = (i + 1) % seg
                    f = [c, j * seg + i, j * seg + i2] if rev else [c, j * seg + i2, j * seg + i]
                    faces.append(f)
    return make_object(name, verts, faces, mat)


def torus(name, major, minor, center, mat, seg=40, rseg=8):
    verts = []
    faces = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        for j in range(rseg):
            b = 2 * math.pi * j / rseg
            r = major + minor * math.cos(b)
            verts.append((r * math.cos(a), r * math.sin(a), center[2] + minor * math.sin(b)))
    for i in range(seg):
        i2 = (i + 1) % seg
        for j in range(rseg):
            j2 = (j + 1) % rseg
            faces.append([i * rseg + j, i2 * rseg + j, i2 * rseg + j2, i * rseg + j2])
    return make_object(name, verts, faces, mat)


def tube(name, pts, radius, mat, sides=6):
    """Tube along polyline points."""
    verts = []
    faces = []
    n = len(pts)
    for k in range(n):
        p = Vector(pts[k])
        if k == 0:
            t = Vector(pts[1]) - p
        elif k == n - 1:
            t = p - Vector(pts[k - 1])
        else:
            t = Vector(pts[k + 1]) - Vector(pts[k - 1])
        t.normalize()
        ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        u = t.cross(ref).normalized()
        v = t.cross(u).normalized()
        for i in range(sides):
            a = 2 * math.pi * i / sides
            q = p + u * (radius * math.cos(a)) + v * (radius * math.sin(a))
            verts.append(q)
    for k in range(n - 1):
        for i in range(sides):
            i2 = (i + 1) % sides
            faces.append([k * sides + i, k * sides + i2, (k + 1) * sides + i2, (k + 1) * sides + i])
    # end caps
    for k, rev in ((0, True), (n - 1, False)):
        c = len(verts)
        verts.append(Vector(pts[k]))
        for i in range(sides):
            i2 = (i + 1) % sides
            a, b = k * sides + i, k * sides + i2
            faces.append([c, a, b] if rev else [c, b, a])
    return make_object(name, verts, faces, mat)


def uv_sphere(name, center, radius, mat, scale=(1, 1, 1), seg=12, rings=6):
    verts = [(center[0], center[1], center[2] + radius * scale[2])]
    faces = []
    for r in range(1, rings):
        phi = math.pi * r / rings
        for i in range(seg):
            a = 2 * math.pi * i / seg
            verts.append((center[0] + radius * scale[0] * math.sin(phi) * math.cos(a),
                          center[1] + radius * scale[1] * math.sin(phi) * math.sin(a),
                          center[2] + radius * scale[2] * math.cos(phi)))
    verts.append((center[0], center[1], center[2] - radius * scale[2]))
    for i in range(seg):
        faces.append([0, 1 + i, 1 + (i + 1) % seg])
    for r in range(rings - 2):
        for i in range(seg):
            i2 = (i + 1) % seg
            faces.append([1 + r * seg + i, 1 + (r + 1) * seg + i,
                          1 + (r + 1) * seg + i2, 1 + r * seg + i2])
    last = len(verts) - 1
    base = 1 + (rings - 2) * seg
    for i in range(seg):
        faces.append([last, base + (i + 1) % seg, base + i])
    return make_object(name, verts, faces, mat)


def build_model():
    red = make_material("Vermilion_Lacquer", (0.75, 0.10, 0.04), 0.0, 0.25)
    dark_red = make_material("Deep_Red_Cord", (0.55, 0.02, 0.03))
    black = make_material("Black_Cord", (0.02, 0.02, 0.03))
    ivory = make_material("Ivory_Membrane", (0.96, 0.92, 0.78))
    gold = make_material("Gold_Metal", (0.95, 0.70, 0.12), 1.0, 0.3)
    leather = make_material("Hoop_Leather", (0.35, 0.18, 0.08))
    wood = make_material("Inner_Wood", (0.45, 0.22, 0.10))

    H = 0.125          # half height
    R_END = 0.095
    R_WAIST = 0.032
    T = 0.006

    # Outer hourglass body
    prof_out = []
    N = 24
    for k in range(N + 1):
        z = -H + 2 * H * k / N
        prof_out.append((body_radius(z, H, R_END, R_WAIST), z))
    # Inner shell (hollow visible at the ends) - build as continuous profile
    prof = []
    prof.append((R_END - T * 2.2, -H - 0.004))
    prof.append((R_END + 0.004, -H - 0.004))
    for (r, z) in prof_out:
        prof.append((r + 0.004 * 0 + 0.0, z))
    prof[2:2 + len(prof_out)] = prof_out
    prof.append((R_END + 0.004, H + 0.004))
    prof.append((R_END - T * 2.2, H + 0.004))
    lathe("Drum_Body_Outer", prof, red, seg=40)

    inner = [(r - T, z) for (r, z) in prof_out]
    inner_prof = [(r, z) for (r, z) in inner]
    lathe("Drum_Body_Inner", inner_prof, wood, seg=32)

    # Rims at each end
    for s, nm in ((1, "Top"), (-1, "Bottom")):
        torus("Rim_Lip_" + nm, R_END, 0.006, (0, 0, s * (H + 0.003)), red, seg=48)

        # Membrane disc
        zc = s * (H + 0.001)
        disc = [(0.0, zc), (R_END - 0.005, zc)]
        lathe("Drumhead_" + nm, [(0.0, zc + s * 0.002), (R_END - 0.004, zc + s * 0.0005),
                                 (R_END - 0.004, zc - s * 0.002)], ivory, seg=40, close_ends=False)
        # Center patch ring (dark smoke patch)
        torus("Head_Ring_" + nm, R_END * 0.45, 0.002, (0, 0, zc + s * 0.0025), dark_red, seg=36, rseg=6)

        # Hoop (leather/metal ring beyond head) with flare
        torus("Head_Hoop_" + nm, R_END + 0.018, 0.005, (0, 0, s * (H + 0.012)), leather, seg=48)
        torus("Metal_Band_" + nm, R_END + 0.003, 0.0035, (0, 0, s * (H - 0.012)), gold, seg=48, rseg=6)
        torus("Metal_Band_Lower_" + nm, R_END - 0.010, 0.003, (0, 0, s * (H - 0.045)), gold, seg=48, rseg=6)

    # Waist metal collar
    torus("Waist_Collar", R_WAIST + 0.002, 0.004, (0, 0, 0), gold, seg=32, rseg=6)

    # Cords: zigzag between top and bottom hoops, bow slightly around waist
    ncord = 12
    zt = H + 0.012
    rt = R_END + 0.018
    for i in range(ncord):
        a0 = 2 * math.pi * i / ncord
        a1 = a0 + math.pi / ncord
        mat = black if i % 2 == 0 else dark_red
        pts = []
        steps = 14
        for k in range(steps + 1):
            t = k / steps
            z = zt - 2 * zt * t
            ang = a0 + (a1 - a0) * t
            bz = abs(z) if abs(z) < H else H
            r = body_radius(bz, H, R_END, R_WAIST) + 0.007
            if abs(z) > H:
                r = rt
            pts.append((r * math.cos(ang), r * math.sin(ang), z))
        tube("Tension_Cord_%02d" % i, pts, 0.0028, mat, sides=6)
        # second pass of cord going back for zigzag
        pts2 = []
        for k in range(steps + 1):
            t = k / steps
            z = -zt + 2 * zt * t
            ang = a1 + (a0 + 2 * math.pi / ncord - a1) * t
            bz = abs(z) if abs(z) < H else H
            r = body_radius(bz, H, R_END, R_WAIST) + 0.007
            if abs(z) > H:
                r = rt
            pts2.append((r * math.cos(ang), r * math.sin(ang), z))
        tube("Tension_Cord_Return_%02d" % i, pts2, 0.0028, black if i % 2 else dark_red, sides=6)

    # Decorative gold studs along hoops
    for s, nm in ((1, "T"), (-1, "B")):
        for i in range(ncord):
            a = 2 * math.pi * (i + 0.5) / ncord
            r = R_END + 0.018
            uv_sphere("Hoop_Stud_%s_%02d" % (nm, i),
                      (r * math.cos(a), r * math.sin(a), s * (H + 0.012)),
                      0.0048, gold, scale=(1, 1, 0.8))

    # Binding cord wrap at waist (squeeze cord, red)
    torus("Waist_Binding_Cord", R_WAIST + 0.009, 0.004, (0, 0, 0.0), dark_red, seg=32, rseg=6)
    # Gold decorative medallions on body
    for i in range(4):
        a = 2 * math.pi * i / 4 + math.pi / 4
        for s, nm in ((1, "U"), (-1, "L")):
            z = s * 0.075
            r = body_radius(z, H, R_END, R_WAIST)
            uv_sphere("Body_Medallion_%s_%d" % (nm, i),
                      ((r + 0.003) * math.cos(a), (r + 0.003) * math.sin(a), z),
                      0.007, gold, scale=(0.6, 0.6, 1))

    # Lift whole model so it sits near origin on ground (drum center at z=0.15)
    for ob in bpy.context.collection.objects:
        pass
