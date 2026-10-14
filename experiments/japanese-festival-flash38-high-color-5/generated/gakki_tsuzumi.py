"""
Procedural 3D Model of a Japanese Tsuzumi Hand Drum for Blender 5.2.
Constructs a detailed, authentic hourglass-shaped drum with deep vermilion
lacquered wooden body, two ivory leather drumheads, contrasting red and black
braided tension cords (tate-shirabe and yoko-shirabe), heavy lacquered curved rims,
gold maki-e crest inlays, and polished brass fittings.
"""

import math
import bpy
import mathutils

# ---------------------------------------------------------------------------
# COLOR PALETTE CONSTANTS
# Both diffuse_color and Principled BSDF Base Color are set to matching RGBA
# to ensure rich, contrasting visuals in Workbench and Eevee/Cycles.
# ---------------------------------------------------------------------------
RGBA_VERMILION = (0.85, 0.14, 0.06, 1.0)
RGBA_GOLD = (0.95, 0.76, 0.15, 1.0)
RGBA_BLACK_LACQUER = (0.05, 0.05, 0.055, 1.0)
RGBA_IVORY_HEAD = (0.92, 0.88, 0.78, 1.0)
RGBA_LEATHER_PATCH = (0.74, 0.61, 0.44, 1.0)
RGBA_RED_CORD = (0.88, 0.18, 0.08, 1.0)
RGBA_BLACK_CORD = (0.08, 0.08, 0.09, 1.0)
RGBA_BRASS = (0.90, 0.72, 0.22, 1.0)


# ---------------------------------------------------------------------------
# MATERIAL CREATION HELPER
# ---------------------------------------------------------------------------
def create_material(name, rgba, roughness=0.3, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.diffuse_color = rgba
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = rgba
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
    return mat


# ---------------------------------------------------------------------------
# MESH GENERATION HELPERS
# ---------------------------------------------------------------------------
def create_mesh_object(name, verts, faces, material=None, parent=None):
    mesh = bpy.data.meshes.new(name=name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    if hasattr(mesh, "shade_smooth"):
        mesh.shade_smooth()
    else:
        for poly in mesh.polygons:
            poly.use_smooth = True

    obj = bpy.data.objects.new(name, mesh)
    if material is not None:
        obj.data.materials.append(material)
    if parent is not None:
        obj.parent = parent

    bpy.context.scene.collection.objects.link(obj)
    return obj


def create_lathe_mesh(name, profile, segments=48, material=None, parent=None, flip_normals=False):
    verts = []
    faces = []
    n_prof = len(profile)

    for r, z in profile:
        for s in range(segments):
            theta = 2.0 * math.pi * s / segments
            verts.append((r * math.cos(theta), r * math.sin(theta), z))

    for i in range(n_prof - 1):
        for s in range(segments):
            s_next = (s + 1) % segments
            v0 = i * segments + s
            v1 = i * segments + s_next
            v2 = (i + 1) * segments + s_next
            v3 = (i + 1) * segments + s
            if flip_normals:
                faces.append((v0, v3, v2, v1))
            else:
                faces.append((v0, v1, v2, v3))

    return create_mesh_object(name=name, verts=verts, faces=faces, material=material, parent=parent)


def create_disc_mesh(name, radius, center_z, dome_height=0.0, rings=6, segments=32, material=None, parent=None, flip_normals=False):
    verts = []
    faces = []

    z_tip = center_z + dome_height
    verts.append((0.0, 0.0, z_tip))

    for ring in range(1, rings + 1):
        frac = ring / rings
        r = radius * frac
        z = center_z + dome_height * (1.0 - frac * frac)
        for s in range(segments):
            theta = 2.0 * math.pi * s / segments
            verts.append((r * math.cos(theta), r * math.sin(theta), z))

    for s in range(segments):
        s_next = (s + 1) % segments
        v_center = 0
        v1 = 1 + s
        v2 = 1 + s_next
        if flip_normals:
            faces.append((v_center, v2, v1))
        else:
            faces.append((v_center, v1, v2))

    for ring in range(1, rings):
        r_curr = 1 + (ring - 1) * segments
        r_next = 1 + ring * segments
        for s in range(segments):
            s_next = (s + 1) % segments
            v0 = r_curr + s
            v1 = r_curr + s_next
            v2 = r_next + s_next
            v3 = r_next + s
            if flip_normals:
                faces.append((v0, v3, v2, v1))
            else:
                faces.append((v0, v1, v2, v3))

    return create_mesh_object(name=name, verts=verts, faces=faces, material=material, parent=parent)


def create_tube_mesh(name, path, radius, segments=8, closed=False, material=None, parent=None):
    if len(path) < 2:
        return None

    verts = []
    faces = []
    ring_centers = [mathutils.Vector(p) for p in path]
    num_pts = len(ring_centers)

    tangents = []
    for i in range(num_pts):
        if i == 0:
            t = (ring_centers[1] - ring_centers[0]).normalized()
        elif i == num_pts - 1:
            t = (ring_centers[-1] - ring_centers[-2]).normalized()
        else:
            t = (ring_centers[i + 1] - ring_centers[i - 1]).normalized()
        tangents.append(t)

    normals = []
    init_up = mathutils.Vector((0, 0, 1))
    if abs(tangents[0].dot(init_up)) > 0.9:
        init_up = mathutils.Vector((0, 1, 0))
    n0 = tangents[0].cross(init_up).normalized()
    normals.append(n0)

    for i in range(1, num_pts):
        t_prev = tangents[i - 1]
        t_curr = tangents[i]
        n_prev = normals[-1]
        axis = t_prev.cross(t_curr)
        if axis.length > 1e-5:
            axis.normalize()
            angle = t_prev.angle(t_curr)
            rot = mathutils.Matrix.Rotation(angle, 3, axis)
            n_curr = (rot @ n_prev).normalized()
        else:
            n_curr = n_prev
        normals.append(n_curr)

    for i in range(num_pts):
        c = ring_centers[i]
        t = tangents[i]
        n = normals[i]
        b = t.cross(n).normalized()
        for s in range(segments):
            ang = 2.0 * math.pi * s / segments
            offset = (n * math.cos(ang) + b * math.sin(ang)) * radius
            verts.append((c.x + offset.x, c.y + offset.y, c.z + offset.z))

    segments_to_bridge = num_pts - 1
    for i in range(segments_to_bridge):
        for s in range(segments):
            s_next = (s + 1) % segments
            v0 = i * segments + s
            v1 = i * segments + s_next
            v2 = (i + 1) * segments + s_next
            v3 = (i + 1) * segments + s
            faces.append((v0, v1, v2, v3))

    if not closed:
        v_start_cap = [s for s in range(segments - 1, -1, -1)]
        faces.append(tuple(v_start_cap))
        end_offset = (num_pts - 1) * segments
        v_end_cap = [end_offset + s for s in range(segments)]
        faces.append(tuple(v_end_cap))

    return create_mesh_object(name=name, verts=verts, faces=faces, material=material, parent=parent)


def create_torus_mesh(name, major_r, minor_r, major_segs=24, minor_segs=10, center=(0.0, 0.0, 0.0), rot_axis='Z', material=None, parent=None):
    verts = []
    faces = []
    cx, cy, cz = center

    for i in range(major_segs):
        theta = 2.0 * math.pi * i / major_segs
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        for j in range(minor_segs):
            phi = 2.0 * math.pi * j / minor_segs
            cos_p = math.cos(phi)
            sin_p = math.sin(phi)

            r = major_r + minor_r * cos_p
            px = r * cos_t
            py = r * sin_t
            pz = minor_r * sin_p

            if rot_axis == 'X':
                x, y, z = px + cx, pz + cy, -py + cz
            elif rot_axis == 'Y':
                x, y, z = pz + cx, py + cy, -px + cz
            else:
                x, y, z = px + cx, py + cy, pz + cz
            verts.append((x, y, z))

    for i in range(major_segs):
        i_next = (i + 1) % major_segs
        for j in range(minor_segs):
            j_next = (j + 1) % minor_segs
            v0 = i * minor_segs + j
            v1 = i_next * minor_segs + j
            v2 = i_next * minor_segs + j_next
            v3 = i * minor_segs + j_next
            faces.append((v0, v1, v2, v3))

    return create_mesh_object(name=name, verts=verts, faces=faces, material=material, parent=parent)


def create_rivet_mesh(name, radius, height, center=(0.0, 0.0, 0.0), normal=(0.0, 0.0, 1.0), material=None, parent=None):
    norm_vec = mathutils.Vector(normal).normalized()
    up_vec = mathutils.Vector((0, 0, 1))
    rot_diff = up_vec.rotation_difference(norm_vec)

    cx, cy, cz = center
    verts = []
    faces = []
    segs = 12

    local_pts = [(0.0, 0.0, height)]
    for s in range(segs):
        ang = 2.0 * math.pi * s / segs
        local_pts.append((radius * 0.7 * math.cos(ang), radius * 0.7 * math.sin(ang), height * 0.7))
    for s in range(segs):
        ang = 2.0 * math.pi * s / segs
        local_pts.append((radius * math.cos(ang), radius * math.sin(ang), 0.0))

    for lx, ly, lz in local_pts:
        v_world = mathutils.Vector((cx, cy, cz)) + (rot_diff @ mathutils.Vector((lx, ly, lz)))
        verts.append((v_world.x, v_world.y, v_world.z))

    for s in range(segs):
        s_next = (s + 1) % segs
        faces.append((0, 1 + s, 1 + s_next))

    for s in range(segs):
        s_next = (s + 1) % segs
        v0 = 1 + s
        v1 = 1 + s_next
        v2 = 1 + segs + s_next
        v3 = 1 + segs + s
        faces.append((v0, v1, v2, v3))

    base_cap = [1 + segs + s for s in range(segs - 1, -1, -1)]
    faces.append(tuple(base_cap))

    return create_mesh_object(name=name, verts=verts, faces=faces, material=material, parent=parent)


def create_crest_mesh(name, size, center=(0.0, 0.0, 0.0), outward_dir=(1.0, 0.0, 0.0), material=None, parent=None):
    cx, cy, cz = center
    norm = mathutils.Vector(outward_dir).normalized()
    up = mathutils.Vector((0, 0, 1))
    if abs(norm.dot(up)) > 0.9:
        up = mathutils.Vector((0, 1, 0))
    tang = norm.cross(up).normalized()
    binorm = norm.cross(tang).normalized()

    verts = []
    faces = []

    v_center = mathutils.Vector((cx, cy, cz)) + norm * (size * 0.35)
    verts.append((v_center.x, v_center.y, v_center.z))

    for i in range(8):
        ang = 2.0 * math.pi * i / 8.0
        r = size if (i % 2 == 0) else size * 0.45
        p = mathutils.Vector((cx, cy, cz)) + (tang * math.cos(ang) + binorm * math.sin(ang)) * r
        verts.append((p.x, p.y, p.z))

    for i in range(8):
        i_next = (i + 1) % 8
        faces.append((0, 1 + i, 1 + i_next))

    return create_mesh_object(name=name, verts=verts, faces=faces, material=material, parent=parent)


# ---------------------------------------------------------------------------
# MAIN MODEL BUILDER
# ---------------------------------------------------------------------------
def build_model():
    root = bpy.data.objects.new("Tsuzumi_Hand_Drum", None)
    bpy.context.scene.collection.objects.link(root)

    mat_vermilion = create_material(name="Mat_Vermilion_Lacquer", rgba=RGBA_VERMILION, roughness=0.15, metallic=0.0)
    mat_gold = create_material(name="Mat_Gold_Makie", rgba=RGBA_GOLD, roughness=0.25, metallic=0.85)
    mat_black_lacquer = create_material(name="Mat_Black_Lacquer", rgba=RGBA_BLACK_LACQUER, roughness=0.12, metallic=0.0)
    mat_ivory = create_material(name="Mat_Ivory_Drumhead", rgba=RGBA_IVORY_HEAD, roughness=0.55, metallic=0.0)
    mat_leather_patch = create_material(name="Mat_Leather_Patch", rgba=RGBA_LEATHER_PATCH, roughness=0.60, metallic=0.0)
    mat_red_cord = create_material(name="Mat_Red_Braided_Cord", rgba=RGBA_RED_CORD, roughness=0.65, metallic=0.0)
    mat_black_cord = create_material(name="Mat_Black_Braided_Cord", rgba=RGBA_BLACK_CORD, roughness=0.65, metallic=0.0)
    mat_brass = create_material(name="Mat_Brass_Fittings", rgba=RGBA_BRASS, roughness=0.20, metallic=0.90)

    # -----------------------------------------------------------------------
    # 1. HOURGLASS WOODEN BODY (Do / 胴)
    # A single continuous closed profile lathed with 64 segments.
    # -----------------------------------------------------------------------
    body_profile = []

    # Bottom Lip (inner -> outer)
    body_profile.append((0.680, -1.100))
    body_profile.append((0.720, -1.120))
    body_profile.append((0.820, -1.120))
    body_profile.append((0.825, -1.090))
    body_profile.append((0.810, -1.050))

    # Lower Bell Flare (going upward from -1.05 to -0.15)
    for i in range(16, -1, -1):
        u = i / 16.0
        z = -(0.15 + u * (1.05 - 0.15))
        r = 0.335 + 0.450 * (0.6 * u + 0.4 * (u ** 2.2))
        body_profile.append((r, z))

    # Waist Moldings (going upward from -0.15 to +0.15)
    body_profile.append((0.355, -0.110))
    body_profile.append((0.330, -0.070))
    body_profile.append((0.345, -0.040))
    body_profile.append((0.315, 0.000))
    body_profile.append((0.345, 0.040))
    body_profile.append((0.330, 0.070))
    body_profile.append((0.355, 0.110))
    body_profile.append((0.335, 0.150))

    # Upper Bell Flare (going upward from +0.15 to +1.05)
    for i in range(17):
        u = i / 16.0
        z = 0.15 + u * (1.05 - 0.15)
        r = 0.335 + 0.450 * (0.6 * u + 0.4 * (u ** 2.2))
        body_profile.append((r, z))

    # Top Lip (outer -> inner)
    body_profile.append((0.810, 1.050))
    body_profile.append((0.825, 1.090))
    body_profile.append((0.820, 1.120))
    body_profile.append((0.720, 1.120))
    body_profile.append((0.680, 1.100))

    # Inner Cavity (going downward from +1.10 to -1.10)
    for i in range(16, -1, -1):
        u = i / 16.0
        z = 1.10 * u
        r_in = 0.160 + 0.520 * (u ** 1.6)
        body_profile.append((r_in, z))

    for i in range(1, 17):
        u = i / 16.0
        z = -1.10 * u
        r_in = 0.160 + 0.520 * (u ** 1.6)
        body_profile.append((r_in, z))

    create_lathe_mesh(name="Body_Hourglass_Vermilion", profile=body_profile, segments=64, material=mat_vermilion, parent=root, flip_normals=False)

    # -----------------------------------------------------------------------
    # 2. GOLD MAKI-E RINGS & EMBELLISHMENTS ON BODY
    # -----------------------------------------------------------------------
    create_torus_mesh(name="Makie_Ring_Waist_Upper", major_r=0.347, minor_r=0.007, major_segs=48, minor_segs=8, center=(0.0, 0.0, 0.04), rot_axis='Z', material=mat_gold, parent=root)
    create_torus_mesh(name="Makie_Ring_Waist_Center", major_r=0.318, minor_r=0.006, major_segs=48, minor_segs=8, center=(0.0, 0.0, 0.00), rot_axis='Z', material=mat_gold, parent=root)
    create_torus_mesh(name="Makie_Ring_Waist_Lower", major_r=0.347, minor_r=0.007, major_segs=48, minor_segs=8, center=(0.0, 0.0, -0.04), rot_axis='Z', material=mat_gold, parent=root)

    create_torus_mesh(name="Makie_Hoop_Upper_A", major_r=0.525, minor_r=0.008, major_segs=48, minor_segs=8, center=(0.0, 0.0, 0.65), rot_axis='Z', material=mat_gold, parent=root)
    create_torus_mesh(name="Makie_Hoop_Upper_B", major_r=0.735, minor_r=0.008, major_segs=48, minor_segs=8, center=(0.0, 0.0, 0.95), rot_axis='Z', material=mat_gold, parent=root)
    create_torus_mesh(name="Makie_Hoop_Lower_A", major_r=0.525, minor_r=0.008, major_segs=48, minor_segs=8, center=(0.0, 0.0, -0.65), rot_axis='Z', material=mat_gold, parent=root)
    create_torus_mesh(name="Makie_Hoop_Lower_B", major_r=0.735, minor_r=0.008, major_segs=48, minor_segs=8, center=(0.0, 0.0, -0.95), rot_axis='Z', material=mat_gold, parent=root)

    for m in range(6):
        psi = m * (2.0 * math.pi / 6.0) + (math.pi / 6.0)
        cx = 0.62 * math.cos(psi)
        cy = 0.62 * math.sin(psi)
        create_crest_mesh(name=f"Makie_Crest_Upper_{m}", size=0.052, center=(cx, cy, 0.78), outward_dir=(math.cos(psi), math.sin(psi), 0.32), material=mat_gold, parent=root)
        create_crest_mesh(name=f"Makie_Crest_Lower_{m}", size=0.052, center=(cx, cy, -0.78), outward_dir=(math.cos(psi), math.sin(psi), -0.32), material=mat_gold, parent=root)

    # -----------------------------------------------------------------------
    # 3. DRUMHEAD CURVED RIMS (Fuchi / 縁)
    # Heavy lacquered iron-and-leather hoops framing the membranes.
    # -----------------------------------------------------------------------
    top_rim_profile = [
        (1.050, 1.160),
        (1.060, 1.210),
        (1.050, 1.260),
        (1.010, 1.290),
        (0.780, 1.290),
        (0.750, 1.270),
        (0.750, 1.150),
        (0.780, 1.140),
        (1.010, 1.140),
        (1.050, 1.160),
    ]
    create_lathe_mesh(name="Rim_Top_Black_Lacquer", profile=top_rim_profile, segments=48, material=mat_black_lacquer, parent=root, flip_normals=False)

    bot_rim_profile = [(r, -z) for r, z in top_rim_profile]
    create_lathe_mesh(name="Rim_Bottom_Black_Lacquer", profile=bot_rim_profile, segments=48, material=mat_black_lacquer, parent=root, flip_normals=True)

    # -----------------------------------------------------------------------
    # 4. IVORY DRUMHEAD MEMBRANES (Kawa / 革) & TUNING PATCHES
    # -----------------------------------------------------------------------
    create_disc_mesh(name="Drumhead_Top_Ivory", radius=0.78, center_z=1.25, dome_height=0.025, rings=6, segments=36, material=mat_ivory, parent=root, flip_normals=False)
    create_disc_mesh(name="Drumhead_Bottom_Ivory", radius=0.78, center_z=-1.25, dome_height=-0.025, rings=6, segments=36, material=mat_ivory, parent=root, flip_normals=True)

    create_disc_mesh(name="Patch_Top_Leather", radius=0.26, center_z=1.276, dome_height=0.005, rings=3, segments=24, material=mat_leather_patch, parent=root, flip_normals=False)
    create_disc_mesh(name="Patch_Bottom_Leather", radius=0.26, center_z=-1.276, dome_height=-0.005, rings=3, segments=24, material=mat_leather_patch, parent=root, flip_normals=True)

    # -----------------------------------------------------------------------
    # 5. RIM FITTINGS: BRASS EYELETS & PERIMETER RIVETS
    # -----------------------------------------------------------------------
    r_holes = 0.92
    for k in range(8):
        theta_k = k * (math.pi / 4.0)
        ex_top = r_holes * math.cos(theta_k)
        ey_top = r_holes * math.sin(theta_k)
        create_torus_mesh(name=f"Eyelet_Top_{k}", major_r=0.038, minor_r=0.012, major_segs=16, minor_segs=8, center=(ex_top, ey_top, 1.21), rot_axis='Z', material=mat_brass, parent=root)

        phi_k = (k + 0.5) * (math.pi / 4.0)
        ex_bot = r_holes * math.cos(phi_k)
        ey_bot = r_holes * math.sin(phi_k)
        create_torus_mesh(name=f"Eyelet_Bottom_{k}", major_r=0.038, minor_r=0.012, major_segs=16, minor_segs=8, center=(ex_bot, ey_bot, -1.21), rot_axis='Z', material=mat_brass, parent=root)

    for j in range(16):
        psi = j * (2.0 * math.pi / 16.0) + (math.pi / 16.0)
        rx = 1.055 * math.cos(psi)
        ry = 1.055 * math.sin(psi)
        create_rivet_mesh(name=f"Rivet_Top_{j}", radius=0.018, height=0.012, center=(rx, ry, 1.21), normal=(math.cos(psi), math.sin(psi), 0.0), material=mat_brass, parent=root)
        create_rivet_mesh(name=f"Rivet_Bottom_{j}", radius=0.018, height=0.012, center=(rx, ry, -1.21), normal=(math.cos(psi), math.sin(psi), 0.0), material=mat_brass, parent=root)

    # -----------------------------------------------------------------------
    # 6. TAUT CONTRASTING BRAIDED TENSION CORDS (Tate-shirabe)
    # 8 Vermilion Red diagonal strands + 8 Black diagonal strands form the
    # iconic crisscrossing hourglass cage.
    # -----------------------------------------------------------------------
    n_samples = 14
    for k in range(8):
        theta_start = k * (math.pi / 4.0)
        phi_end = (k + 0.5) * (math.pi / 4.0)

        # Downward Red Tension Cord
        red_pts = []
        for s in range(n_samples):
            t = s / (n_samples - 1)
            z = 1.21 - 2.42 * t
            ang = theta_start + (phi_end - theta_start) * t
            u = abs(z) / 1.21
            r = 0.385 + 0.535 * (0.35 * u + 0.65 * (u ** 1.8))
            red_pts.append((r * math.cos(ang), r * math.sin(ang), z))
        create_tube_mesh(name=f"Cord_Tate_Red_{k}", path=red_pts, radius=0.016, segments=8, closed=False, material=mat_red_cord, parent=root)

        # Upward Black Tension Cord
        phi_start = (k + 0.5) * (math.pi / 4.0)
        theta_next = (k + 1.0) * (math.pi / 4.0)
        black_pts = []
        for s in range(n_samples):
            t = s / (n_samples - 1)
            z = -1.21 + 2.42 * t
            ang = phi_start + (theta_next - phi_start) * t
            u = abs(z) / 1.21
            r = 0.385 + 0.535 * (0.35 * u + 0.65 * (u ** 1.8))
            black_pts.append((r * math.cos(ang), r * math.sin(ang), z))
        create_tube_mesh(name=f"Cord_Tate_Black_{k}", path=black_pts, radius=0.016, segments=8, closed=False, material=mat_black_cord, parent=root)

    # -----------------------------------------------------------------------
    # 7. HORIZONTAL WAIST WINDING CORDS (Yoko-shirabe)
    # Tightly coiling black braided cords clamping the vertical tension cage.
    # -----------------------------------------------------------------------
    coil_pts = []
    n_coil_steps = 72
    total_rotations = 4.0
    for s in range(n_coil_steps):
        t = s / (n_coil_steps - 1)
        ang = total_rotations * 2.0 * math.pi * t
        z = -0.10 + 0.20 * t
        r = 0.410 + 0.007 * math.cos(16.0 * ang)
        coil_pts.append((r * math.cos(ang), r * math.sin(ang), z))
    create_tube_mesh(name="Cord_Yoko_Coil_Black", path=coil_pts, radius=0.015, segments=8, closed=False, material=mat_black_cord, parent=root)

    # -----------------------------------------------------------------------
    # 8. MASTER ORNAMENTAL KNOT (Tsuzumi-musubi) & HANGING TASSELS
    # Distinct front ceremonial knot with butterfly loop wings and cascading
    # red and black cord tails with brass ferrules.
    # -----------------------------------------------------------------------
    clasp_pts = [(0.435, 0.0, -0.11), (0.435, 0.0, 0.11)]
    create_tube_mesh(name="Knot_Clasp_Black", path=clasp_pts, radius=0.024, segments=8, closed=False, material=mat_black_cord, parent=root)
    create_torus_mesh(name="Knot_Ring_Brass", major_r=0.032, minor_r=0.008, major_segs=16, minor_segs=8, center=(0.435, 0.0, 0.0), rot_axis='Y', material=mat_brass, parent=root)

    # Left & Right Red Butterfly Knot Loops
    left_wing_pts = [
        (0.435, 0.02, 0.04),
        (0.460, 0.10, 0.09),
        (0.470, 0.18, 0.05),
        (0.460, 0.15, -0.04),
        (0.435, 0.02, -0.02),
    ]
    create_tube_mesh(name="Knot_Wing_Left_Red", path=left_wing_pts, radius=0.014, segments=8, closed=False, material=mat_red_cord, parent=root)

    right_wing_pts = [
        (0.435, -0.02, 0.04),
        (0.460, -0.10, 0.09),
        (0.470, -0.18, 0.05),
        (0.460, -0.15, -0.04),
        (0.435, -0.02, -0.02),
    ]
    create_tube_mesh(name="Knot_Wing_Right_Red", path=right_wing_pts, radius=0.014, segments=8, closed=False, material=mat_red_cord, parent=root)

    # Hanging Cord 1: Vermilion Red
    hang_red_pts = [
        (0.435, 0.02, -0.06),
        (0.460, 0.05, -0.22),
        (0.490, 0.04, -0.42),
        (0.520, 0.07, -0.62),
        (0.540, 0.05, -0.80),
    ]
    create_tube_mesh(name="Cord_Hanging_Red", path=hang_red_pts, radius=0.013, segments=8, closed=False, material=mat_red_cord, parent=root)
    create_tube_mesh(name="Ferrule_Red_Brass", path=[(0.540, 0.05, -0.80), (0.542, 0.05, -0.84)], radius=0.018, segments=8, closed=False, material=mat_brass, parent=root)
    create_tube_mesh(name="Tassel_Tip_Red", path=[(0.542, 0.05, -0.84), (0.545, 0.05, -0.92)], radius=0.024, segments=8, closed=False, material=mat_red_cord, parent=root)

    # Hanging Cord 2: Contrasting Deep Black
    hang_black_pts = [
        (0.435, -0.02, -0.06),
        (0.460, -0.04, -0.18),
        (0.485, -0.07, -0.36),
        (0.510, -0.05, -0.54),
        (0.530, -0.08, -0.70),
    ]
    create_tube_mesh(name="Cord_Hanging_Black", path=hang_black_pts, radius=0.013, segments=8, closed=False, material=mat_black_cord, parent=root)
    create_tube_mesh(name="Ferrule_Black_Brass", path=[(0.530, -0.08, -0.70), (0.532, -0.08, -0.74)], radius=0.018, segments=8, closed=False, material=mat_brass, parent=root)
    create_tube_mesh(name="Tassel_Tip_Black", path=[(0.532, -0.08, -0.74), (0.535, -0.08, -0.81)], radius=0.024, segments=8, closed=False, material=mat_black_cord, parent=root)

    # -----------------------------------------------------------------------
    # 9. TUNING SLIDERS (Chōshi-chō / 金具)
    # Brass tuning rings sliding along the cords to tune acoustic pitch.
    # -----------------------------------------------------------------------
    for k_slide in (0, 2, 4, 6):
        theta_s = k_slide * (math.pi / 4.0)
        phi_s = (k_slide + 0.5) * (math.pi / 4.0)
        t_slide = (1.21 - 0.52) / 2.42
        ang_s = theta_s + (phi_s - theta_s) * t_slide
        u_s = 0.52 / 1.21
        r_s = 0.385 + 0.535 * (0.35 * u_s + 0.65 * (u_s ** 1.8))
        sx = r_s * math.cos(ang_s)
        sy = r_s * math.sin(ang_s)
        create_torus_mesh(name=f"Tuning_Slider_Brass_{k_slide}", major_r=0.026, minor_r=0.007, major_segs=16, minor_segs=8, center=(sx, sy, 0.52), rot_axis='Z', material=mat_brass, parent=root)

    return root
