"""
Procedural 3D Japanese Wagasa Umbrella Generator for Blender 5.2.
Constructs an authentic traditional oil-paper wagasa with 36 bamboo ribs,
radial spokes, Janome (bullseye) concentric crimson and cream washi canopy,
gold accents, intricate silk thread embroidery (kagari-ito), carved wooden shaft,
rattan-wrapped handle, brass ferrules, spring catches, and decorative top rosette.
"""

import math
import bpy


def create_wagasa_material(name, rgba, roughness=0.4, metallic=0.0):
    """Creates a material and guarantees matching diffuse_color and Principled BSDF Base Color."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.diffuse_color = rgba

    bsdf = None
    if mat.node_tree:
        for node in mat.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                bsdf = node
                break
        if bsdf is None:
            bsdf = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')

        bsdf.inputs["Base Color"].default_value = rgba
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic

    return mat


def create_mesh_object(name, verts, faces, collection, mat=None):
    """Creates a tangible mesh object from pydata, attaches material, and links to collection."""
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    if mat is not None:
        obj.data.materials.append(mat)

    collection.objects.link(obj)
    return obj


def get_canopy_point(r, theta, is_midpoint, z_offset=0.0):
    """Computes a 3D coordinate on the wagasa canopy including pleated sag between ribs."""
    t = (r - 0.035) / (0.460 - 0.035)
    t = max(0.0, min(1.0, t))
    base_z = 0.700 - 0.205 * (t ** 1.18)

    if is_midpoint:
        rad_factor = 1.0 - 0.014 * t
        sag_z = -0.0055 * t
    else:
        rad_factor = 1.0
        sag_z = 0.0

    eff_r = r * rad_factor
    x = eff_r * math.cos(theta)
    y = eff_r * math.sin(theta)
    z = base_z + sag_z + z_offset
    return (x, y, z)


def create_canopy_band(name, r_min, r_max, r_steps, mat, collection, num_ribs=36, thickness=0.0008, is_innermost=False, is_outermost=False):
    """Creates a solid, two-sided annular washi paper band with subtle pleated faceting."""
    verts = []
    faces = []
    total_ang = num_ribs * 2
    pts_per_layer = (r_steps + 1) * total_ang

    # Generate Top Layer (+thickness/2)
    for s in range(r_steps + 1):
        r = r_min + (r_max - r_min) * (s / float(r_steps))
        for i in range(num_ribs):
            theta_rib = 2.0 * math.pi * i / float(num_ribs)
            theta_mid = 2.0 * math.pi * (i + 0.5) / float(num_ribs)
            verts.append(get_canopy_point(r=r, theta=theta_rib, is_midpoint=False, z_offset=thickness * 0.5))
            verts.append(get_canopy_point(r=r, theta=theta_mid, is_midpoint=True, z_offset=thickness * 0.5))

    # Generate Bottom Layer (-thickness/2)
    for s in range(r_steps + 1):
        r = r_min + (r_max - r_min) * (s / float(r_steps))
        for i in range(num_ribs):
            theta_rib = 2.0 * math.pi * i / float(num_ribs)
            theta_mid = 2.0 * math.pi * (i + 0.5) / float(num_ribs)
            verts.append(get_canopy_point(r=r, theta=theta_rib, is_midpoint=False, z_offset=-thickness * 0.5))
            verts.append(get_canopy_point(r=r, theta=theta_mid, is_midpoint=True, z_offset=-thickness * 0.5))

    # Top Faces (pointing UP)
    for s in range(r_steps):
        for j in range(total_ang):
            j_next = (j + 1) % total_ang
            v0 = s * total_ang + j
            v1 = (s + 1) * total_ang + j
            v2 = (s + 1) * total_ang + j_next
            v3 = s * total_ang + j_next
            faces.append((v0, v1, v2, v3))

    # Bottom Faces (pointing DOWN)
    bot_off = pts_per_layer
    for s in range(r_steps):
        for j in range(total_ang):
            j_next = (j + 1) % total_ang
            v0 = bot_off + s * total_ang + j
            v1 = bot_off + s * total_ang + j_next
            v2 = bot_off + (s + 1) * total_ang + j_next
            v3 = bot_off + (s + 1) * total_ang + j
            faces.append((v0, v1, v2, v3))

    # Inner Boundary Rim Wall
    if is_innermost:
        for j in range(total_ang):
            j_next = (j + 1) % total_ang
            t0 = j
            t1 = j_next
            b0 = bot_off + j
            b1 = bot_off + j_next
            faces.append((t0, t1, b1, b0))

    # Outer Boundary Rim Wall
    if is_outermost:
        for j in range(total_ang):
            j_next = (j + 1) % total_ang
            t0 = r_steps * total_ang + j
            t1 = r_steps * total_ang + j_next
            b0 = bot_off + r_steps * total_ang + j
            b1 = bot_off + r_steps * total_ang + j_next
            faces.append((t0, b0, b1, t1))

    return create_mesh_object(name=name, verts=verts, faces=faces, collection=collection, mat=mat)


def add_box_beam(p1, p2, width, height, verts, faces):
    """Builds a solid 4-sided prismatic beam connecting two 3D coordinates."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-6:
        return

    d = (dx / length, dy / length, dz / length)

    ref = (1.0, 0.0, 0.0) if abs(d[2]) > 0.95 else (0.0, 0.0, 1.0)
    ux = d[1] * ref[2] - d[2] * ref[1]
    uy = d[2] * ref[0] - d[0] * ref[2]
    uz = d[0] * ref[1] - d[1] * ref[0]
    u_len = math.sqrt(ux * ux + uy * uy + uz * uz)
    u = (ux / u_len, uy / u_len, uz / u_len)

    vx = u[1] * d[2] - u[2] * d[1]
    vy = u[2] * d[0] - u[0] * d[2]
    vz = u[0] * d[1] - u[1] * d[0]
    v = (vx, vy, vz)

    hw = width * 0.5
    hh = height * 0.5
    base = len(verts)

    # 4 vertices around p1
    verts.append((p1[0] + hw * u[0] + hh * v[0], p1[1] + hw * u[1] + hh * v[1], p1[2] + hw * u[2] + hh * v[2]))
    verts.append((p1[0] - hw * u[0] + hh * v[0], p1[1] - hw * u[1] + hh * v[1], p1[2] - hw * u[2] + hh * v[2]))
    verts.append((p1[0] - hw * u[0] - hh * v[0], p1[1] - hw * u[1] - hh * v[1], p1[2] - hw * u[2] - hh * v[2]))
    verts.append((p1[0] + hw * u[0] - hh * v[0], p1[1] + hw * u[1] - hh * v[1], p1[2] + hw * u[2] - hh * v[2]))

    # 4 vertices around p2
    verts.append((p2[0] + hw * u[0] + hh * v[0], p2[1] + hw * u[1] + hh * v[1], p2[2] + hw * u[2] + hh * v[2]))
    verts.append((p2[0] - hw * u[0] + hh * v[0], p2[1] - hw * u[1] + hh * v[1], p2[2] - hw * u[2] + hh * v[2]))
    verts.append((p2[0] - hw * u[0] - hh * v[0], p2[1] - hw * u[1] - hh * v[1], p2[2] - hw * u[2] - hh * v[2]))
    verts.append((p2[0] + hw * u[0] - hh * v[0], p2[1] + hw * u[1] - hh * v[1], p2[2] + hw * u[2] - hh * v[2]))

    # 4 longitudinal faces
    faces.append((base + 0, base + 4, base + 5, base + 1))
    faces.append((base + 1, base + 5, base + 6, base + 2))
    faces.append((base + 2, base + 6, base + 7, base + 3))
    faces.append((base + 3, base + 7, base + 4, base + 0))

    # End caps
    faces.append((base + 0, base + 1, base + 2, base + 3))
    faces.append((base + 4, base + 7, base + 6, base + 5))


def build_ribs(collection, mat, num_ribs=36):
    """Builds 36 thin split bamboo main ribs (oya-bone) along the canopy curve."""
    verts = []
    faces = []
    r_samples = [0.024, 0.075, 0.150, 0.245, 0.330, 0.410, 0.460, 0.472]
    w_base = 0.0034
    h_base = 0.0028

    for i in range(num_ribs):
        theta = 2.0 * math.pi * i / float(num_ribs)
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)

        u_phi_x = -sin_t
        u_phi_y = cos_t
        rib_start = len(verts)
        num_slices = len(r_samples)

        for r in r_samples:
            pt = get_canopy_point(r=r, theta=theta, is_midpoint=False, z_offset=-0.0019)
            cx, cy, cz = pt

            w = w_base if r <= 0.460 else w_base * 0.65
            h = h_base if r <= 0.460 else h_base * 0.75

            v0 = (cx + 0.5 * w * u_phi_x, cy + 0.5 * w * u_phi_y, cz + 0.5 * h)
            v1 = (cx - 0.5 * w * u_phi_x, cy - 0.5 * w * u_phi_y, cz + 0.5 * h)
            v2 = (cx - 0.5 * w * u_phi_x, cy - 0.5 * w * u_phi_y, cz - 0.5 * h)
            v3 = (cx + 0.5 * w * u_phi_x, cy + 0.5 * w * u_phi_y, cz - 0.5 * h)
            verts.extend([v0, v1, v2, v3])

        for s_idx in range(num_slices - 1):
            b0 = rib_start + s_idx * 4
            b1 = rib_start + (s_idx + 1) * 4
            faces.append((b0 + 0, b1 + 0, b1 + 1, b0 + 1))
            faces.append((b0 + 1, b1 + 1, b1 + 2, b0 + 2))
            faces.append((b0 + 2, b1 + 2, b1 + 3, b0 + 3))
            faces.append((b0 + 3, b1 + 3, b1 + 0, b0 + 0))

        # Start and end caps
        c0 = rib_start
        faces.append((c0 + 0, c0 + 3, c0 + 2, c0 + 1))
        c_end = rib_start + (num_slices - 1) * 4
        faces.append((c_end + 0, c_end + 1, c_end + 2, c_end + 3))

    return create_mesh_object(name="Wagasa_Ribs_Bamboo", verts=verts, faces=faces, collection=collection, mat=mat)


def build_spokes(collection, mat, num_ribs=36):
    """Builds 36 bamboo support spokes (ko-bone) connecting the runner hub to ribs."""
    verts = []
    faces = []

    for i in range(num_ribs):
        theta = 2.0 * math.pi * i / float(num_ribs)
        p_hub = (0.022 * math.cos(theta), 0.022 * math.sin(theta), 0.455)
        p_rib = get_canopy_point(r=0.245, theta=theta, is_midpoint=False, z_offset=-0.0035)

        # Main spoke bar
        add_box_beam(p1=p_hub, p2=p_rib, width=0.0030, height=0.0028, verts=verts, faces=faces)

        # Hinge joint bracket wrapping around rib
        c_x = p_rib[0]
        c_y = p_rib[1]
        c_z = p_rib[2]
        p_j1 = (c_x - 0.004 * math.cos(theta), c_y - 0.004 * math.sin(theta), c_z - 0.001)
        p_j2 = (c_x + 0.004 * math.cos(theta), c_y + 0.004 * math.sin(theta), c_z + 0.001)
        add_box_beam(p1=p_j1, p2=p_j2, width=0.0062, height=0.0062, verts=verts, faces=faces)

    return create_mesh_object(name="Wagasa_Spokes_Bamboo", verts=verts, faces=faces, collection=collection, mat=mat)


def build_thread_bindings(collection, mat_gold, mat_indigo, mat_white, num_ribs=36):
    """Creates traditional 3-tier silk embroidery (kagari-ito) web underneath the canopy."""
    spokes = []
    for i in range(num_ribs):
        theta = 2.0 * math.pi * i / float(num_ribs)
        p_hub = (0.022 * math.cos(theta), 0.022 * math.sin(theta), 0.455)
        p_rib = get_canopy_point(r=0.245, theta=theta, is_midpoint=False, z_offset=-0.0035)
        spokes.append((p_hub, p_rib))

    def get_spoke_pt(spoke_idx, t):
        p0, p1 = spokes[spoke_idx % num_ribs]
        return (
            p0[0] + (p1[0] - p0[0]) * t,
            p0[1] + (p1[1] - p0[1]) * t,
            p0[2] + (p1[2] - p0[2]) * t,
        )

    # 1. Gold Silk Thread Inner Diamond Web
    g_verts, g_faces = [], []
    for i in range(num_ribs):
        i_next = (i + 1) % num_ribs
        pt_a0 = get_spoke_pt(i, 0.26)
        pt_a1 = get_spoke_pt(i_next, 0.26)
        pt_b0 = get_spoke_pt(i, 0.33)
        pt_b1 = get_spoke_pt(i_next, 0.33)

        add_box_beam(p1=pt_a0, p2=pt_a1, width=0.0012, height=0.0012, verts=g_verts, faces=g_faces)
        add_box_beam(p1=pt_b0, p2=pt_b1, width=0.0012, height=0.0012, verts=g_verts, faces=g_faces)
        add_box_beam(p1=pt_a0, p2=pt_b1, width=0.0011, height=0.0011, verts=g_verts, faces=g_faces)
        add_box_beam(p1=pt_b0, p2=pt_a1, width=0.0011, height=0.0011, verts=g_verts, faces=g_faces)

    create_mesh_object(name="Wagasa_Thread_Gold", verts=g_verts, faces=g_faces, collection=collection, mat=mat_gold)

    # 2. Indigo Silk Thread Star Lattice
    ind_verts, ind_faces = [], []
    for i in range(num_ribs):
        i_1 = (i + 1) % num_ribs
        i_2 = (i + 2) % num_ribs
        pt_m0 = get_spoke_pt(i, 0.48)
        pt_m1 = get_spoke_pt(i_1, 0.48)
        pt_h0 = get_spoke_pt(i, 0.56)
        pt_h2 = get_spoke_pt(i_2, 0.56)

        add_box_beam(p1=pt_m0, p2=pt_m1, width=0.0013, height=0.0013, verts=ind_verts, faces=ind_faces)
        add_box_beam(p1=pt_m0, p2=pt_h2, width=0.0012, height=0.0012, verts=ind_verts, faces=ind_faces)
        add_box_beam(p1=pt_h0, p2=get_spoke_pt(i_1, 0.56), width=0.0013, height=0.0013, verts=ind_verts, faces=ind_faces)

    create_mesh_object(name="Wagasa_Thread_Indigo", verts=ind_verts, faces=ind_faces, collection=collection, mat=mat_indigo)

    # 3. White Silk Thread Concentric Outer Web & Hinge Ties
    w_verts, w_faces = [], []
    for i in range(num_ribs):
        i_next = (i + 1) % num_ribs
        pt_w0 = get_spoke_pt(i, 0.72)
        pt_w1 = get_spoke_pt(i_next, 0.72)
        pt_w2 = get_spoke_pt(i, 0.79)
        pt_w3 = get_spoke_pt(i_next, 0.79)

        add_box_beam(p1=pt_w0, p2=pt_w1, width=0.0012, height=0.0012, verts=w_verts, faces=w_faces)
        add_box_beam(p1=pt_w2, p2=pt_w3, width=0.0012, height=0.0012, verts=w_verts, faces=w_faces)
        add_box_beam(p1=pt_w0, p2=pt_w2, width=0.0014, height=0.0014, verts=w_verts, faces=w_faces)

    create_mesh_object(name="Wagasa_Thread_White", verts=w_verts, faces=w_faces, collection=collection, mat=mat_white)


def create_lathe_mesh(name, profile, segments, mat, collection):
    """Generates a rotational revolved mesh around the Z-axis with outward facing normals."""
    verts = []
    faces = []
    num_prof = len(profile)

    for r, z in profile:
        if r < 1e-5:
            verts.append((0.0, 0.0, z))
        else:
            for s in range(segments):
                theta = 2.0 * math.pi * s / float(segments)
                verts.append((r * math.cos(theta), r * math.sin(theta), z))

    vert_offsets = []
    curr = 0
    for r, _ in profile:
        vert_offsets.append(curr)
        curr += 1 if r < 1e-5 else segments

    for p in range(num_prof - 1):
        r0, _ = profile[p]
        r1, _ = profile[p + 1]
        off0 = vert_offsets[p]
        off1 = vert_offsets[p + 1]

        if r0 < 1e-5 and r1 >= 1e-5:
            for s in range(segments):
                s_next = (s + 1) % segments
                faces.append((off0, off1 + s_next, off1 + s))
        elif r0 >= 1e-5 and r1 < 1e-5:
            for s in range(segments):
                s_next = (s + 1) % segments
                faces.append((off0 + s, off0 + s_next, off1))
        elif r0 >= 1e-5 and r1 >= 1e-5:
            for s in range(segments):
                s_next = (s + 1) % segments
                faces.append((off0 + s, off0 + s_next, off1 + s_next, off1 + s))

    return create_mesh_object(name=name, verts=verts, faces=faces, collection=collection, mat=mat)


def build_turned_components(collection, mat_brass, mat_rattan, mat_dark_wood):
    """Builds the handle, carved shaft nodes, hubs, ferrules, and wooden finial."""
    # 1. Base Brass End Cap (Ishitsuki)
    base_cap_profile = [
        (0.000, -0.082),
        (0.007, -0.080),
        (0.012, -0.075),
        (0.0135, -0.065),
        (0.0145, -0.062),
        (0.0145, -0.058),
        (0.0132, -0.055),
        (0.0110, -0.055),
    ]
    create_lathe_mesh(name="Wagasa_Handle_Brass_Cap", profile=base_cap_profile, segments=24, mat=mat_brass, collection=collection)

    # 2. Carved Rattan Cane Grip
    rattan_profile = []
    for k in range(29):
        frac = k / 28.0
        z = -0.055 + 0.155 * frac
        r = 0.0132 + 0.0016 * math.sin(frac * 14.0 * math.pi)
        rattan_profile.append((r, z))
    create_lathe_mesh(name="Wagasa_Handle_Rattan", profile=rattan_profile, segments=24, mat=mat_rattan, collection=collection)

    # 3. Handle Top Brass Collar
    brass_collar_profile = [
        (0.0110, 0.100),
        (0.0142, 0.102),
        (0.0142, 0.108),
        (0.0110, 0.110),
    ]
    create_lathe_mesh(name="Wagasa_Handle_Brass_Collar", profile=brass_collar_profile, segments=24, mat=mat_brass, collection=collection)

    # 4. Main Bamboo Shaft with 3 Raised Nodes
    shaft_profile = [
        (0.0110, 0.110),
        (0.0110, 0.230),
        (0.0126, 0.240),
        (0.0110, 0.250),
        (0.0110, 0.390),
        (0.0126, 0.400),
        (0.0110, 0.410),
        (0.0110, 0.570),
        (0.0126, 0.580),
        (0.0110, 0.590),
        (0.0110, 0.685),
    ]
    create_lathe_mesh(name="Wagasa_Shaft_Wood", profile=shaft_profile, segments=24, mat=mat_dark_wood, collection=collection)

    # 5. Runner Hub (Shita-rokuro)
    runner_profile = [
        (0.0115, 0.440),
        (0.0180, 0.442),
        (0.0240, 0.447),
        (0.0240, 0.473),
        (0.0180, 0.478),
        (0.0115, 0.480),
    ]
    create_lathe_mesh(name="Wagasa_Runner_Hub", profile=runner_profile, segments=36, mat=mat_dark_wood, collection=collection)

    # 6. Top Hub (Kami-rokuro)
    top_hub_profile = [
        (0.0115, 0.685),
        (0.0200, 0.688),
        (0.0260, 0.695),
        (0.0260, 0.718),
        (0.0180, 0.722),
        (0.0120, 0.725),
    ]
    create_lathe_mesh(name="Wagasa_Top_Hub", profile=top_hub_profile, segments=36, mat=mat_dark_wood, collection=collection)

    # 7. Top Hub Brass Retaining Wire Ring
    wire_profile = [
        (0.0255, 0.704),
        (0.0275, 0.706),
        (0.0275, 0.710),
        (0.0255, 0.712),
    ]
    create_lathe_mesh(name="Wagasa_Top_Brass_Wire", profile=wire_profile, segments=36, mat=mat_brass, collection=collection)

    # 8. Wooden Spindle Finial (Atama)
    finial_profile = [
        (0.0120, 0.725),
        (0.0150, 0.740),
        (0.0140, 0.765),
        (0.0160, 0.785),
        (0.0120, 0.810),
        (0.0070, 0.825),
    ]
    create_lathe_mesh(name="Wagasa_Finial_Wood", profile=finial_profile, segments=24, mat=mat_dark_wood, collection=collection)

    # 9. Top Brass Finial Tip
    top_brass_profile = [
        (0.0070, 0.825),
        (0.0085, 0.828),
        (0.0075, 0.840),
        (0.0040, 0.848),
        (0.0000, 0.852),
    ]
    create_lathe_mesh(name="Wagasa_Finial_Brass_Tip", profile=top_brass_profile, segments=20, mat=mat_brass, collection=collection)


def build_rosette(name, r_inner, r_outer_peak, r_outer_valley, z_inner, z_outer, segments, mat, collection):
    """Builds a decorative multi-pleated paper flower collar (dou-bana) around the top hub."""
    verts = []
    faces = []
    num_pts = segments * 2

    for k in range(num_pts):
        theta = 2.0 * math.pi * k / float(num_pts)
        verts.append((r_inner * math.cos(theta), r_inner * math.sin(theta), z_inner))

    for k in range(num_pts):
        theta = 2.0 * math.pi * k / float(num_pts)
        r_out = r_outer_peak if (k % 2 == 0) else r_outer_valley
        z_out = z_outer if (k % 2 == 0) else (z_outer + 0.007)
        verts.append((r_out * math.cos(theta), r_out * math.sin(theta), z_out))

    for k in range(num_pts):
        k_next = (k + 1) % num_pts
        i0 = k
        i1 = k_next
        o1 = num_pts + k_next
        o0 = num_pts + k
        faces.append((i0, o0, o1, i1))
        faces.append((i0, i1, o1, o0))

    return create_mesh_object(name=name, verts=verts, faces=faces, collection=collection, mat=mat)


def build_hanging_cord_loop(collection, mat):
    """Creates the traditional braided hanging loop ring at the top of the umbrella."""
    verts = []
    faces = []
    major_r = 0.012
    minor_r = 0.0022
    cz = 0.860
    num_u = 16
    num_v = 8

    for u_idx in range(num_u):
        phi = 2.0 * math.pi * u_idx / float(num_u)
        cx = major_r * math.cos(phi)
        cz_u = cz + major_r * math.sin(phi)
        nx = math.cos(phi)
        nz = math.sin(phi)

        for v_idx in range(num_v):
            psi = 2.0 * math.pi * v_idx / float(num_v)
            vx = cx + minor_r * math.cos(psi) * nx
            vy = minor_r * math.sin(psi)
            vz = cz_u + minor_r * math.cos(psi) * nz
            verts.append((vx, vy, vz))

    for u_idx in range(num_u):
        u_next = (u_idx + 1) % num_u
        for v_idx in range(num_v):
            v_next = (v_idx + 1) % num_v
            idx0 = u_idx * num_v + v_idx
            idx1 = u_next * num_v + v_idx
            idx2 = u_next * num_v + v_next
            idx3 = u_idx * num_v + v_next
            faces.append((idx0, idx1, idx2, idx3))

    return create_mesh_object(name="Wagasa_Hanging_Cord", verts=verts, faces=faces, collection=collection, mat=mat)


def build_hajiki_springs(collection, mat):
    """Builds the traditional brass spring catches (hajiki) locking the umbrella open."""
    verts = []
    faces = []
    # Lower spring stop right below the runner hub at z = 0.428
    p1 = (0.010, -0.0025, 0.418)
    p2 = (0.015, -0.0025, 0.432)
    add_box_beam(p1=p1, p2=p2, width=0.0035, height=0.0040, verts=verts, faces=faces)

    # Upper spring catch at z = 0.640
    p3 = (0.010, -0.0025, 0.630)
    p4 = (0.015, -0.0025, 0.644)
    add_box_beam(p1=p3, p2=p4, width=0.0035, height=0.0040, verts=verts, faces=faces)

    return create_mesh_object(name="Wagasa_Hajiki_Springs", verts=verts, faces=faces, collection=collection, mat=mat)


def build_model():
    """Main entry point: procedurally builds the complete Japanese wagasa umbrella model."""
    col = bpy.context.scene.collection

    # Materials with explicitly synchronized Workbench diffuse_color and Principled BSDF Base Color
    mat_crimson = create_wagasa_material(name="Wagasa_Canopy_Crimson", rgba=(0.82, 0.06, 0.12, 1.0), roughness=0.52, metallic=0.0)
    mat_cream = create_wagasa_material(name="Wagasa_Canopy_Cream", rgba=(0.95, 0.91, 0.79, 1.0), roughness=0.55, metallic=0.0)
    mat_gold = create_wagasa_material(name="Wagasa_Canopy_Gold", rgba=(0.88, 0.70, 0.18, 1.0), roughness=0.35, metallic=0.2)
    mat_black_rim = create_wagasa_material(name="Wagasa_Canopy_BlackRim", rgba=(0.08, 0.07, 0.07, 1.0), roughness=0.45, metallic=0.0)
    mat_bamboo = create_wagasa_material(name="Wagasa_Bamboo_Natural", rgba=(0.82, 0.70, 0.46, 1.0), roughness=0.48, metallic=0.0)
    mat_dark_wood = create_wagasa_material(name="Wagasa_Dark_Lacquered_Wood", rgba=(0.24, 0.14, 0.08, 1.0), roughness=0.30, metallic=0.0)
    mat_rattan = create_wagasa_material(name="Wagasa_Rattan_Grip", rgba=(0.66, 0.52, 0.35, 1.0), roughness=0.58, metallic=0.0)
    mat_brass = create_wagasa_material(name="Wagasa_Brass_Fittings", rgba=(0.90, 0.74, 0.28, 1.0), roughness=0.25, metallic=0.8)
    mat_th_gold = create_wagasa_material(name="Wagasa_Silk_Thread_Gold", rgba=(0.96, 0.68, 0.12, 1.0), roughness=0.35, metallic=0.1)
    mat_th_indigo = create_wagasa_material(name="Wagasa_Silk_Thread_Indigo", rgba=(0.12, 0.42, 0.68, 1.0), roughness=0.40, metallic=0.0)
    mat_th_white = create_wagasa_material(name="Wagasa_Silk_Thread_White", rgba=(0.96, 0.96, 0.96, 1.0), roughness=0.42, metallic=0.0)
    mat_cord = create_wagasa_material(name="Wagasa_Braided_Cord", rgba=(0.72, 0.10, 0.14, 1.0), roughness=0.50, metallic=0.0)

    # 1. Canopy Concentric Washi Paper Bands (Janome pattern: Crimson -> Gold -> Cream -> Crimson -> Black Rim)
    create_canopy_band(name="Wagasa_Canopy_InnerCrimson", r_min=0.035, r_max=0.150, r_steps=3, mat=mat_crimson, collection=col, num_ribs=36, thickness=0.0008, is_innermost=True, is_outermost=False)
    create_canopy_band(name="Wagasa_Canopy_GoldBand", r_min=0.150, r_max=0.170, r_steps=1, mat=mat_gold, collection=col, num_ribs=36, thickness=0.0008, is_innermost=False, is_outermost=False)
    create_canopy_band(name="Wagasa_Canopy_CreamBand", r_min=0.170, r_max=0.330, r_steps=3, mat=mat_cream, collection=col, num_ribs=36, thickness=0.0008, is_innermost=False, is_outermost=False)
    create_canopy_band(name="Wagasa_Canopy_OuterCrimson", r_min=0.330, r_max=0.445, r_steps=3, mat=mat_crimson, collection=col, num_ribs=36, thickness=0.0008, is_innermost=False, is_outermost=False)
    create_canopy_band(name="Wagasa_Canopy_FukurinRim", r_min=0.445, r_max=0.460, r_steps=1, mat=mat_black_rim, collection=col, num_ribs=36, thickness=0.0008, is_innermost=False, is_outermost=True)

    # 2. Structural Bamboo Skeleton: 36 Main Ribs & 36 Support Spokes
    build_ribs(collection=col, mat=mat_bamboo, num_ribs=36)
    build_spokes(collection=col, mat=mat_bamboo, num_ribs=36)

    # 3. Traditional Multi-colored Silk Thread Embroidery Underneath Canopy (Kagari-ito)
    build_thread_bindings(collection=col, mat_gold=mat_th_gold, mat_indigo=mat_th_indigo, mat_white=mat_th_white, num_ribs=36)

    # 4. Central Turned Shaft, Rattan Handle, Carved Wooden Hubs, and Brass Ferrules
    build_turned_components(collection=col, mat_brass=mat_brass, mat_rattan=mat_rattan, mat_dark_wood=mat_dark_wood)

    # 5. Traditional Decorative Top Paper Rosette (Dou-bana)
    build_rosette(name="Wagasa_Doubana_Cream", r_inner=0.016, r_outer_peak=0.062, r_outer_valley=0.046, z_inner=0.730, z_outer=0.686, segments=12, mat=mat_cream, collection=col)
    build_rosette(name="Wagasa_Doubana_Crimson", r_inner=0.016, r_outer_peak=0.048, r_outer_valley=0.036, z_inner=0.735, z_outer=0.700, segments=12, mat=mat_crimson, collection=col)

    # 6. Brass Spring Stops (Hajiki) & Braided Hanging Loop Cord
    build_hajiki_springs(collection=col, mat=mat_brass)
    build_hanging_cord_loop(collection=col, mat=mat_cord)
