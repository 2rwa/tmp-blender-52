"""
Procedural 3D Japanese Folding Sensu Fan (扇子) Model Generator.
Designed and targeted for Blender 5.2.2.

Features:
- Fully opened Japanese sensu fan geometry with 142-degree angular span.
- Physically folded 3D accordion washi paper leaf with crisp mountain/valley pleats.
- Multi-material decorative geometric panels: Aizome Indigo Blue, Vermilion Scarlet,
  warm Washi Ivory, and gleaming Kinpaku Gold Leaf.
- 19 distinct structural bamboo ribs: 17 inner tapered ribs (naka-bone) and 2 heavy
  outer guard sticks (oya-bone) with curved tips and polished dark urushi lacquer.
- Detailed Kaname (pivot rivet) hardware assembly with central pin and rosette washers.
- Fukurin lacquered dark edge binding framing the top pleated perimeter.
- Suspended Kazari-himo silk cord with traditional Agemaki knot and fluted tassel.
- Full compatibility with Blender Workbench shading.color_type='MATERIAL'.
"""

import bpy
import math
import mathutils


# -----------------------------------------------------------------------------
# Configuration & Proportions
# -----------------------------------------------------------------------------

NUM_RIBS = 19               # Total bamboo ribs (2 guard sticks + 17 inner ribs)
NUM_PLEATS = 18             # Number of accordion fold panels across leaf
RADIAL_DIVS = 12            # Radial ring subdivisions for geometric leaf panels
INNER_RADIUS = 0.105        # Throat radius where paper leaf begins (meters)
OUTER_RADIUS = 0.255        # Outer perimeter radius of paper leaf (meters)
FAN_SPAN_DEG = 142.0        # Total open fan angle in degrees
PLEAT_AMPLITUDE_MAX = 0.0055 # Max peak-to-valley displacement at outer rim (meters)
PAPER_HALF_THICK = 0.00025  # Half thickness of the solid washi paper leaf (meters)


# -----------------------------------------------------------------------------
# Core Helpers
# -----------------------------------------------------------------------------

def create_material(name, rgba, roughness=0.5, metallic=0.0):
    """
    Creates a material with exact matching Workbench diffuse_color
    and Principled BSDF Base Color for Blender 5.2.2.
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.diffuse_color = rgba
    
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf is not None:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = rgba
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
            
    return mat


def create_mesh_object(name, verts, faces, materials=None, face_materials=None, smooth=False):
    """
    Builds a distinct editable mesh object directly from pydata, links it
    to the active scene collection, and sets polygon smooth flags and materials.
    """
    mesh = bpy.data.meshes.new(name=name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    if smooth:
        for poly in mesh.polygons:
            poly.use_smooth = True

    if face_materials is not None and len(face_materials) == len(mesh.polygons):
        for poly_idx, mat_idx in enumerate(face_materials):
            mesh.polygons[poly_idx].material_index = mat_idx

    obj = bpy.data.objects.new(name=name, object_data=mesh)
    bpy.context.scene.collection.objects.link(obj)

    if materials:
        for mat in materials:
            obj.data.materials.append(mat)

    return obj


# -----------------------------------------------------------------------------
# Component Generators
# -----------------------------------------------------------------------------

def build_paper_leaf(materials):
    """
    Constructs the 3D pleated washi paper leaf with manifold solid thickness,
    crisp accordion fold topology, and geometric decorative panel coloring.
    """
    span_rad = math.radians(FAN_SPAN_DEG)
    start_rad = (math.pi - span_rad) * 0.5
    verts = []

    # Front surface vertices
    for j in range(RADIAL_DIVS + 1):
        r = INNER_RADIUS + (j / RADIAL_DIVS) * (OUTER_RADIUS - INNER_RADIUS)
        amp = PLEAT_AMPLITUDE_MAX * (r / OUTER_RADIUS)
        for k in range(NUM_RIBS):
            th = start_rad + (k / (NUM_RIBS - 1)) * span_rad
            z = amp if (k % 2 == 0) else -amp
            x = r * math.cos(th)
            y = r * math.sin(th)
            verts.append((x, y, z + PAPER_HALF_THICK))

    # Back surface vertices
    back_offset = len(verts)
    for j in range(RADIAL_DIVS + 1):
        r = INNER_RADIUS + (j / RADIAL_DIVS) * (OUTER_RADIUS - INNER_RADIUS)
        amp = PLEAT_AMPLITUDE_MAX * (r / OUTER_RADIUS)
        for k in range(NUM_RIBS):
            th = start_rad + (k / (NUM_RIBS - 1)) * span_rad
            z = amp if (k % 2 == 0) else -amp
            x = r * math.cos(th)
            y = r * math.sin(th)
            verts.append((x, y, z - PAPER_HALF_THICK))

    faces = []
    face_materials = []

    # 1. Front pleated faces with geometric Japanese motifs
    for j in range(RADIAL_DIVS):
        for k in range(NUM_RIBS - 1):
            v0 = j * NUM_RIBS + k
            v1 = (j + 1) * NUM_RIBS + k
            v2 = (j + 1) * NUM_RIBS + (k + 1)
            v3 = j * NUM_RIBS + (k + 1)
            faces.append((v0, v1, v2, v3))

            # Geometric material assignment
            # 0: Ivory, 1: Indigo, 2: Scarlet, 3: Gold, 4: Dark Lacquer
            if j == 11 or j == 8 or j == 3:
                # Gilded metallic divider arcs and rim
                m_idx = 3
            elif j < 3:
                # Lower band: Deep Indigo base with central Ivory/Scarlet crest
                if j == 1 and k in (8, 9):
                    m_idx = 0
                elif j == 1 and k in (7, 10):
                    m_idx = 2
                else:
                    m_idx = 1
            elif 4 <= j <= 7:
                # Mid band: Dan-chigai diagonal stepped chevron panels
                diag = (k + (j - 4) * 2) % 6
                if diag in (0, 1):
                    m_idx = 2
                elif diag in (2, 3):
                    m_idx = 0
                else:
                    m_idx = 1
            else:
                # Upper band: Alternating geometric blocks of Indigo and Scarlet
                block = (k // 3) % 2
                if block == 0:
                    m_idx = 1 if j == 10 else 2
                else:
                    m_idx = 2 if j == 10 else 1
                if (k % 3 == 1) and (j == 9):
                    m_idx = 0
            face_materials.append(m_idx)

    # 2. Back faces (plain mulberry washi paper texture)
    for j in range(RADIAL_DIVS):
        for k in range(NUM_RIBS - 1):
            v0 = back_offset + j * NUM_RIBS + k
            v1 = back_offset + j * NUM_RIBS + (k + 1)
            v2 = back_offset + (j + 1) * NUM_RIBS + (k + 1)
            v3 = back_offset + (j + 1) * NUM_RIBS + k
            faces.append((v0, v1, v2, v3))
            face_materials.append(0)

    # 3. Bottom rim boundary closure
    for k in range(NUM_RIBS - 1):
        f0 = k
        f1 = k + 1
        b1 = back_offset + k + 1
        b0 = back_offset + k
        faces.append((f0, f1, b1, b0))
        face_materials.append(4)

    # 4. Top outer rim boundary closure
    for k in range(NUM_RIBS - 1):
        f0 = RADIAL_DIVS * NUM_RIBS + k
        f1 = RADIAL_DIVS * NUM_RIBS + (k + 1)
        b1 = back_offset + RADIAL_DIVS * NUM_RIBS + (k + 1)
        b0 = back_offset + RADIAL_DIVS * NUM_RIBS + k
        faces.append((f0, b0, b1, f1))
        face_materials.append(4)

    # 5. Right outer edge closure (k = 0)
    for j in range(RADIAL_DIVS):
        f0 = j * NUM_RIBS
        f1 = (j + 1) * NUM_RIBS
        b1 = back_offset + (j + 1) * NUM_RIBS
        b0 = back_offset + j * NUM_RIBS
        faces.append((f0, b0, b1, f1))
        face_materials.append(4)

    # 6. Left outer edge closure (k = NUM_RIBS - 1)
    for j in range(RADIAL_DIVS):
        f0 = j * NUM_RIBS + (NUM_RIBS - 1)
        f1 = (j + 1) * NUM_RIBS + (NUM_RIBS - 1)
        b1 = back_offset + (j + 1) * NUM_RIBS + (NUM_RIBS - 1)
        b0 = back_offset + j * NUM_RIBS + (NUM_RIBS - 1)
        faces.append((f0, f1, b1, b0))
        face_materials.append(4)

    return create_mesh_object(
        name="Sensu_Paper_Leaf",
        verts=verts,
        faces=faces,
        materials=materials,
        face_materials=face_materials,
        smooth=False
    )


def build_rim_binding(material):
    """
    Constructs the Fukurin (protective dark lacquered edge binding)
    following the zigzag contour of the top accordion edge.
    """
    span_rad = math.radians(FAN_SPAN_DEG)
    start_rad = (math.pi - span_rad) * 0.5
    verts = []
    faces = []

    r_in = OUTER_RADIUS - 0.0022
    r_out = OUTER_RADIUS + 0.0012
    th_rim = PAPER_HALF_THICK + 0.00045

    for k in range(NUM_RIBS):
        th = start_rad + (k / (NUM_RIBS - 1)) * span_rad
        z_ctr = PLEAT_AMPLITUDE_MAX if (k % 2 == 0) else -PLEAT_AMPLITUDE_MAX
        c_th = math.cos(th)
        s_th = math.sin(th)

        verts.append((r_in * c_th, r_in * s_th, z_ctr + th_rim))
        verts.append((r_out * c_th, r_out * s_th, z_ctr + th_rim))
        verts.append((r_out * c_th, r_out * s_th, z_ctr - th_rim))
        verts.append((r_in * c_th, r_in * s_th, z_ctr - th_rim))

    for k in range(NUM_RIBS - 1):
        b0 = k * 4
        b1 = (k + 1) * 4
        faces.append((b0 + 0, b1 + 0, b1 + 1, b0 + 1))
        faces.append((b0 + 1, b1 + 1, b1 + 2, b0 + 2))
        faces.append((b0 + 2, b1 + 2, b1 + 3, b0 + 3))
        faces.append((b0 + 3, b1 + 3, b1 + 0, b0 + 0))

    # Caps
    faces.append((0, 3, 2, 1))
    last = (NUM_RIBS - 1) * 4
    faces.append((last + 0, last + 1, last + 2, last + 3))

    return create_mesh_object(
        name="Sensu_Rim_Binding",
        verts=verts,
        faces=faces,
        materials=[material],
        smooth=False
    )


def build_inner_ribs(material):
    """
    Constructs the 17 distinct bamboo inner ribs (naka-bone).
    Each rib tapers gracefully from the pivot, bends smoothly to meet the
    pleated paper leaf, and extends along the fold valleys/ridges.
    """
    span_rad = math.radians(FAN_SPAN_DEG)
    start_rad = (math.pi - span_rad) * 0.5
    verts = []
    faces = []

    r_stations = [
        -0.010, -0.004, 0.000, 0.012, 0.035,
        0.065, 0.105, 0.145, 0.185, 0.225, 0.250
    ]

    for k in range(1, NUM_RIBS - 1):
        rib_base_idx = len(verts)
        th = start_rad + (k / (NUM_RIBS - 1)) * span_rad
        c_th = math.cos(th)
        s_th = math.sin(th)
        u_rad = (c_th, s_th, 0.0)
        u_perp = (-s_th, c_th, 0.0)

        z_piv = (k - 9) * 0.00045

        for r in r_stations:
            # Radial interpolation of elevation
            if r <= 0.012:
                z = z_piv
                w = 0.0030
                t = 0.0011
            elif r >= INNER_RADIUS:
                z_target = (PLEAT_AMPLITUDE_MAX * (r / OUTER_RADIUS)) * (1.0 if k % 2 == 0 else -1.0)
                z = z_target - (PAPER_HALF_THICK + 0.00035)
                f_taper = (r - INNER_RADIUS) / (0.250 - INNER_RADIUS)
                w = 0.0022 * (1.0 - f_taper) + 0.0013 * f_taper
                t = 0.00065 * (1.0 - f_taper) + 0.00042 * f_taper
            else:
                f_mid = (r - 0.012) / (INNER_RADIUS - 0.012)
                s = f_mid * f_mid * (3.0 - 2.0 * f_mid)
                z_target_in = (PLEAT_AMPLITUDE_MAX * (INNER_RADIUS / OUTER_RADIUS)) * (1.0 if k % 2 == 0 else -1.0)
                z_target_in -= (PAPER_HALF_THICK + 0.00035)
                z = (1.0 - s) * z_piv + s * z_target_in
                w = 0.0030 * (1.0 - f_mid) + 0.0022 * f_mid
                t = 0.0011 * (1.0 - f_mid) + 0.00065 * f_mid

            cx = r * u_rad[0]
            cy = r * u_rad[1]
            cz = z

            hw = w * 0.5
            ht = t * 0.5
            verts.append((cx + hw * u_perp[0], cy + hw * u_perp[1], cz + ht))
            verts.append((cx - hw * u_perp[0], cy - hw * u_perp[1], cz + ht))
            verts.append((cx - hw * u_perp[0], cy - hw * u_perp[1], cz - ht))
            verts.append((cx + hw * u_perp[0], cy + hw * u_perp[1], cz - ht))

        num_sections = len(r_stations)
        for s in range(num_sections - 1):
            s0 = rib_base_idx + s * 4
            s1 = rib_base_idx + (s + 1) * 4
            faces.append((s0 + 0, s1 + 0, s1 + 1, s0 + 1))
            faces.append((s0 + 1, s1 + 1, s1 + 2, s0 + 2))
            faces.append((s0 + 2, s1 + 2, s1 + 3, s0 + 3))
            faces.append((s0 + 3, s1 + 3, s1 + 0, s0 + 0))

        # Bottom and top end caps
        faces.append((rib_base_idx + 0, rib_base_idx + 3, rib_base_idx + 2, rib_base_idx + 1))
        top_idx = rib_base_idx + (num_sections - 1) * 4
        faces.append((top_idx + 0, top_idx + 1, top_idx + 2, top_idx + 3))

    return create_mesh_object(
        name="Sensu_Inner_Ribs",
        verts=verts,
        faces=faces,
        materials=[material],
        smooth=True
    )


def build_guard_stick(name, angle_rad, is_left, material):
    """
    Constructs a thick, polished outer guard stick (oya-bone) with authentic
    waist curvature, convex cross-section profile, and inward-curving tip (tame).
    """
    verts = []
    faces = []

    c_th = math.cos(angle_rad)
    s_th = math.sin(angle_rad)
    u_rad = (c_th, s_th, 0.0)
    u_perp = (-s_th, c_th, 0.0)

    r_stations = [
        -0.012, -0.006, 0.000, 0.018, 0.045,
        0.080, 0.105, 0.140, 0.180, 0.220, 0.245, 0.258, 0.265
    ]

    for r in r_stations:
        z_piv = 0.0048 if is_left else -0.0048
        if r <= 0.018:
            z = z_piv
        elif r >= INNER_RADIUS:
            z_target = PLEAT_AMPLITUDE_MAX * (r / OUTER_RADIUS) + (PAPER_HALF_THICK + 0.0012)
            z = z_target
        else:
            u = (r - 0.018) / (INNER_RADIUS - 0.018)
            s = u * u * (3.0 - 2.0 * u)
            z_target_in = PLEAT_AMPLITUDE_MAX * (INNER_RADIUS / OUTER_RADIUS) + (PAPER_HALF_THICK + 0.0012)
            z = (1.0 - s) * z_piv + s * z_target_in

        # Traditional heat-bent inward tip curve (tame)
        if r > 0.180:
            t_tip = (r - 0.180) / (0.265 - 0.180)
            inward_disp = 0.0032 * (t_tip ** 2) * (-1.0 if is_left else 1.0)
        else:
            inward_disp = 0.0

        # Guard stick width and thickness profiles
        if r <= -0.006:
            w = 0.0045
            t = 0.0030
        elif r <= 0.018:
            w = 0.0076
            t = 0.0036
        elif r <= 0.080:
            w = 0.0092
            t = 0.0034
        elif r <= INNER_RADIUS:
            w = 0.0090
            t = 0.0030
        elif r <= 0.220:
            w = 0.0078
            t = 0.0026
        elif r <= 0.245:
            w = 0.0068
            t = 0.0022
        else:
            w = 0.0035
            t = 0.0016

        cx = r * u_rad[0] + inward_disp * u_perp[0]
        cy = r * u_rad[1] + inward_disp * u_perp[1]
        cz = z

        hw = w * 0.5
        ht = t * 0.5
        # 6-vertex convex beveled cross-section
        verts.append((cx + hw * u_perp[0], cy + hw * u_perp[1], cz + ht * 0.6))
        verts.append((cx, cy, cz + ht))
        verts.append((cx - hw * u_perp[0], cy - hw * u_perp[1], cz + ht * 0.6))
        verts.append((cx - hw * u_perp[0], cy - hw * u_perp[1], cz - ht))
        verts.append((cx, cy, cz - ht))
        verts.append((cx + hw * u_perp[0], cy + hw * u_perp[1], cz - ht))

    num_sections = len(r_stations)
    for s in range(num_sections - 1):
        s0 = s * 6
        s1 = (s + 1) * 6
        for p in range(6):
            p_next = (p + 1) % 6
            faces.append((s0 + p, s1 + p, s1 + p_next, s0 + p_next))

    # Caps
    faces.append((0, 5, 4, 3, 2, 1))
    top_base = (num_sections - 1) * 6
    faces.append((top_base + 0, top_base + 1, top_base + 2, top_base + 3, top_base + 4, top_base + 5))

    return create_mesh_object(
        name=name,
        verts=verts,
        faces=faces,
        materials=[material],
        smooth=True
    )


def build_guard_inlay(name, angle_rad, is_left, material):
    """
    Constructs a decorative Kinpaku gold crest inlay plate on the guard stick handle.
    """
    c_th = math.cos(angle_rad)
    s_th = math.sin(angle_rad)
    u_rad = (c_th, s_th, 0.0)
    u_perp = (-s_th, c_th, 0.0)

    z = 0.0068 if is_left else -0.0068
    r_start = 0.035
    r_end = 0.075
    w = 0.0042
    th = 0.00035

    verts = []
    hw = w * 0.5
    for r in (r_start, r_end):
        cx = r * u_rad[0]
        cy = r * u_rad[1]
        verts.append((cx + hw * u_perp[0], cy + hw * u_perp[1], z + th))
        verts.append((cx - hw * u_perp[0], cy - hw * u_perp[1], z + th))
        verts.append((cx - hw * u_perp[0], cy - hw * u_perp[1], z - th))
        verts.append((cx + hw * u_perp[0], cy + hw * u_perp[1], z - th))

    faces = [
        (0, 4, 5, 1),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (3, 7, 4, 0),
        (0, 1, 2, 3),
        (4, 7, 6, 5)
    ]

    return create_mesh_object(
        name=name,
        verts=verts,
        faces=faces,
        materials=[material],
        smooth=False
    )


def build_pivot_hardware(material):
    """
    Constructs the central Kaname (pivot rivet) pin and ornate dual washer rosettes.
    """
    verts = []
    faces = []

    # 1. Central rivet pin cylinder
    radius = 0.0018
    z_min = -0.0095
    z_max = 0.0095
    segs = 12

    for i in range(segs):
        ang = (2.0 * math.pi * i) / segs
        x = radius * math.cos(ang)
        y = radius * math.sin(ang)
        verts.append((x, y, z_max))
        verts.append((x, y, z_min))

    for i in range(segs):
        i_next = (i + 1) % segs
        v0 = i * 2
        v1 = i_next * 2
        v2 = i_next * 2 + 1
        v3 = i * 2 + 1
        faces.append((v0, v1, v2, v3))

    faces.append(tuple(i * 2 for i in range(segs)))
    faces.append(tuple(reversed([i * 2 + 1 for i in range(segs)])))

    # 2. Dual rosette washers (kaname-gane)
    for z_center in (0.0076, -0.0076):
        w_base = len(verts)
        r_inner = 0.0018
        r_outer = 0.0055
        w_th = 0.0011
        z0 = z_center + w_th * 0.5
        z1 = z_center - w_th * 0.5

        for i in range(segs):
            ang = (2.0 * math.pi * i) / segs
            ca = math.cos(ang)
            sa = math.sin(ang)
            verts.append((r_outer * ca, r_outer * sa, z0))
            verts.append((r_outer * ca, r_outer * sa, z1))
            verts.append((r_inner * ca, r_inner * sa, z1))
            verts.append((r_inner * ca, r_inner * sa, z0))

        for i in range(segs):
            i_next = (i + 1) % segs
            p0 = w_base + i * 4
            p1 = w_base + i_next * 4
            faces.append((p0 + 0, p1 + 0, p1 + 1, p0 + 1))  # outer wall
            faces.append((p0 + 3, p0 + 2, p1 + 2, p1 + 3))  # inner wall
            faces.append((p0 + 0, p0 + 3, p1 + 3, p1 + 0))  # top face
            faces.append((p0 + 1, p1 + 1, p1 + 2, p0 + 2))  # bottom face

    return create_mesh_object(
        name="Sensu_Pivot_Rivet",
        verts=verts,
        faces=faces,
        materials=[material],
        smooth=True
    )


def build_tassel_assembly(mat_silk, mat_gold, mat_brass):
    """
    Constructs the hanging silk cord assembly: brass suspension ring,
    traditional Agemaki decorative knot, gilded cap, and fluted silk tassel skirt.
    """
    # 1. Brass suspension eyelet ring
    r_ring_major = 0.0042
    r_ring_minor = 0.00085
    ring_center = (0.0, -0.012, -0.002)
    ring_verts = []
    ring_faces = []

    u_segs = 16
    v_segs = 8
    for i in range(u_segs):
        u_ang = (2.0 * math.pi * i) / u_segs
        cy = ring_center[1] + r_ring_major * math.cos(u_ang)
        cz = ring_center[2] + r_ring_major * math.sin(u_ang)
        for j in range(v_segs):
            v_ang = (2.0 * math.pi * j) / v_segs
            vx = ring_center[0] + r_ring_minor * math.cos(v_ang)
            vy = cy + (r_ring_minor * math.sin(v_ang)) * math.cos(u_ang)
            vz = cz + (r_ring_minor * math.sin(v_ang)) * math.sin(u_ang)
            ring_verts.append((vx, vy, vz))

    for i in range(u_segs):
        i_next = (i + 1) % u_segs
        for j in range(v_segs):
            j_next = (j + 1) % v_segs
            p0 = i * v_segs + j
            p1 = i_next * v_segs + j
            p2 = i_next * v_segs + j_next
            p3 = i * v_segs + j_next
            ring_faces.append((p0, p1, p2, p3))

    create_mesh_object(
        name="Sensu_Tassel_Ring",
        verts=ring_verts,
        faces=ring_faces,
        materials=[mat_brass],
        smooth=True
    )

    # 2. Agemaki decorative silk knot
    knot_verts = []
    knot_faces = []
    
    # Central cushion knot
    kx = 0.0045
    ky = 0.0040
    kz = 0.0022
    kcy = -0.022
    kcz = -0.002
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                knot_verts.append((sx * kx, kcy + sy * ky, kcz + sz * kz))
    
    knot_faces.extend([
        (0, 1, 3, 2), (4, 6, 7, 5),
        (0, 4, 5, 1), (2, 3, 7, 6),
        (0, 2, 6, 4), (1, 5, 7, 3)
    ])

    # Left and right silk ear loops
    for side in (-1.0, 1.0):
        base_v = len(knot_verts)
        loop_r = 0.0045
        loop_thick = 0.0011
        loop_segs = 8
        for i in range(loop_segs):
            ang = (math.pi * i) / (loop_segs - 1)
            lx = side * (0.004 + loop_r * math.sin(ang))
            ly = kcy + loop_r * math.cos(ang)
            lz = kcz
            knot_verts.append((lx, ly - loop_thick, lz))
            knot_verts.append((lx, ly + loop_thick, lz))
            knot_verts.append((lx, ly, lz + loop_thick))
            knot_verts.append((lx, ly, lz - loop_thick))

        for i in range(loop_segs - 1):
            s0 = base_v + i * 4
            s1 = base_v + (i + 1) * 4
            knot_faces.append((s0 + 0, s1 + 0, s1 + 2, s0 + 2))
            knot_faces.append((s0 + 2, s1 + 2, s1 + 1, s0 + 1))
            knot_faces.append((s0 + 1, s1 + 1, s1 + 3, s0 + 3))
            knot_faces.append((s0 + 3, s1 + 3, s1 + 0, s0 + 0))

    create_mesh_object(
        name="Sensu_Tassel_Knot",
        verts=knot_verts,
        faces=knot_faces,
        materials=[mat_silk],
        smooth=True
    )

    # 3. Gilded tassel collar / cap
    cap_verts = []
    cap_faces = []
    cap_segs = 12
    cap_r = 0.0036
    cap_y0 = -0.030
    cap_y1 = -0.035
    for i in range(cap_segs):
        ang = (2.0 * math.pi * i) / cap_segs
        ca = math.cos(ang)
        sa = math.sin(ang)
        cap_verts.append((cap_r * ca, cap_y0, kcz + cap_r * sa))
        cap_verts.append((cap_r * ca, cap_y1, kcz + cap_r * sa))

    for i in range(cap_segs):
        i_next = (i + 1) % cap_segs
        p0 = i * 2
        p1 = i_next * 2
        p2 = i_next * 2 + 1
        p3 = i * 2 + 1
        cap_faces.append((p0, p1, p2, p3))

    cap_faces.append(tuple(i * 2 for i in range(cap_segs)))
    cap_faces.append(tuple(reversed([i * 2 + 1 for i in range(cap_segs)])))

    create_mesh_object(
        name="Sensu_Tassel_Cap",
        verts=cap_verts,
        faces=cap_faces,
        materials=[mat_gold],
        smooth=True
    )

    # 4. Fluted silk tassel fringe skirt
    fringe_verts = []
    fringe_faces = []
    fringe_flutes = 16
    fringe_rings = 5
    y_start = -0.035
    y_end = -0.076

    for r_idx in range(fringe_rings):
        t_ring = r_idx / (fringe_rings - 1)
        cur_y = y_start + t_ring * (y_end - y_start)
        base_r = 0.0034 * (1.0 - t_ring) + 0.0080 * t_ring
        for i in range(fringe_flutes):
            ang = (2.0 * math.pi * i) / fringe_flutes
            flute_amp = 0.00045 * (1.0 - t_ring * 0.3)
            r_flute = base_r + (flute_amp if (i % 2 == 0) else -flute_amp)
            fx = r_flute * math.cos(ang)
            fz = kcz + r_flute * math.sin(ang)
            fringe_verts.append((fx, cur_y, fz))

    for r_idx in range(fringe_rings - 1):
        for i in range(fringe_flutes):
            i_next = (i + 1) % fringe_flutes
            v0 = r_idx * fringe_flutes + i
            v1 = r_idx * fringe_flutes + i_next
            v2 = (r_idx + 1) * fringe_flutes + i_next
            v3 = (r_idx + 1) * fringe_flutes + i
            fringe_faces.append((v0, v1, v2, v3))

    # Bottom hem closure
    bottom_start = (fringe_rings - 1) * fringe_flutes
    fringe_faces.append(tuple(reversed([bottom_start + i for i in range(fringe_flutes)])))

    create_mesh_object(
        name="Sensu_Tassel_Fringe",
        verts=fringe_verts,
        faces=fringe_faces,
        materials=[mat_silk],
        smooth=True
    )


# -----------------------------------------------------------------------------
# Main Assembly Entry Point
# -----------------------------------------------------------------------------

def build_model():
    """
    Constructs the complete Japanese Folding Sensu Fan 3D model.
    Only creates the model components; does not delete or modify existing scene elements.
    """
    # 1. Initialize materials with exact matching diffuse_color & BSDF Base Color
    mat_ivory = create_material(
        name="Sensu_Washi_Ivory",
        rgba=(0.95, 0.92, 0.83, 1.0),
        roughness=0.70,
        metallic=0.0
    )
    mat_indigo = create_material(
        name="Sensu_Indigo_Blue",
        rgba=(0.06, 0.16, 0.42, 1.0),
        roughness=0.55,
        metallic=0.0
    )
    mat_scarlet = create_material(
        name="Sensu_Scarlet_Red",
        rgba=(0.85, 0.12, 0.10, 1.0),
        roughness=0.50,
        metallic=0.0
    )
    mat_gold = create_material(
        name="Sensu_Gold_Leaf",
        rgba=(0.92, 0.75, 0.18, 1.0),
        roughness=0.25,
        metallic=0.85
    )
    mat_lacquer_dark = create_material(
        name="Sensu_Lacquer_Dark",
        rgba=(0.05, 0.04, 0.05, 1.0),
        roughness=0.20,
        metallic=0.05
    )
    mat_bamboo = create_material(
        name="Sensu_Bamboo",
        rgba=(0.80, 0.62, 0.36, 1.0),
        roughness=0.45,
        metallic=0.0
    )
    mat_brass = create_material(
        name="Sensu_Brass",
        rgba=(0.88, 0.70, 0.24, 1.0),
        roughness=0.25,
        metallic=0.90
    )
    mat_crimson_silk = create_material(
        name="Sensu_Crimson_Silk",
        rgba=(0.72, 0.06, 0.14, 1.0),
        roughness=0.40,
        metallic=0.05
    )

    paper_materials = [
        mat_ivory,
        mat_indigo,
        mat_scarlet,
        mat_gold,
        mat_lacquer_dark
    ]

    # 2. Build 3D pleated paper leaf
    build_paper_leaf(materials=paper_materials)

    # 3. Build top dark edge binding (Fukurin)
    build_rim_binding(material=mat_lacquer_dark)

    # 4. Build 17 inner bamboo ribs (Naka-bone)
    build_inner_ribs(material=mat_bamboo)

    # 5. Build left and right lacquered guard sticks (Oya-bone) & gold inlays
    span_rad = math.radians(FAN_SPAN_DEG)
    start_rad = (math.pi - span_rad) * 0.5
    angle_right = start_rad
    angle_left = start_rad + span_rad

    build_guard_stick(
        name="Sensu_Guard_Rib_Right",
        angle_rad=angle_right,
        is_left=False,
        material=mat_lacquer_dark
    )
    build_guard_inlay(
        name="Sensu_Inlay_Right",
        angle_rad=angle_right,
        is_left=False,
        material=mat_gold
    )

    build_guard_stick(
        name="Sensu_Guard_Rib_Left",
        angle_rad=angle_left,
        is_left=True,
        material=mat_lacquer_dark
    )
    build_guard_inlay(
        name="Sensu_Inlay_Left",
        angle_rad=angle_left,
        is_left=True,
        material=mat_gold
    )

    # 6. Build Kaname pivot rivet & rosette washers
    build_pivot_hardware(material=mat_brass)

    # 7. Build suspended silk tassel cord & fringe assembly
    build_tassel_assembly(
        mat_silk=mat_crimson_silk,
        mat_gold=mat_gold,
        mat_brass=mat_brass
    )
