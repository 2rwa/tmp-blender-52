"""
Kagura Suzu (神楽鈴) Procedural 3D Model Generator for Blender 5.2.2.

Creates an authentic Japanese ritual bell wand featuring:
- A lacquered vermilion handle with gold ferrules.
- An ivory-and-crimson silk cord grip wrap (ito-maki style).
- An 8-petaled flared lotus guard (tsuba) and stepped brass collars.
- A 3-tiered brass armature (3-5-7 layout = 15 authentic Suzu bells).
- Detailed crotal bells with equatorial welt, hollow acoustic mouth, and pellet.
- A sacred flame jewel finial (giboshi/hoju) at the peak.
- Five hanging ritual silk streamers (goshikio: Red, White, Yellow, Green, Purple).
"""

import bpy
import math
import mathutils

# ---------------------------------------------------------------------------
# Constants & Color Palette (Workbench Material Diffuse & Principled BSDF)
# ---------------------------------------------------------------------------
COLOR_GOLD = (0.96, 0.76, 0.18, 1.0)
COLOR_GOLD_DARK = (0.80, 0.60, 0.14, 1.0)
COLOR_LACQUER_RED = (0.82, 0.06, 0.04, 1.0)
COLOR_IVORY = (0.92, 0.89, 0.80, 1.0)
COLOR_CRIMSON_CORD = (0.68, 0.04, 0.05, 1.0)

COLOR_RIBBON_RED = (0.88, 0.05, 0.05, 1.0)
COLOR_RIBBON_WHITE = (0.95, 0.95, 0.92, 1.0)
COLOR_RIBBON_YELLOW = (0.96, 0.78, 0.06, 1.0)
COLOR_RIBBON_GREEN = (0.04, 0.58, 0.30, 1.0)
COLOR_RIBBON_PURPLE = (0.44, 0.10, 0.65, 1.0)


# ---------------------------------------------------------------------------
# Helper Functions: Materials and Objects
# ---------------------------------------------------------------------------
def create_material(name, color_rgba, metallic=0.0, roughness=0.4):
    """
    Creates a Blender material setting both diffuse_color (for Workbench)
    and Principled BSDF Base Color identically.
    """
    mat = bpy.data.materials.new(name=name)
    mat.diffuse_color = color_rgba
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = color_rgba
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
    return mat


def create_mesh_object(name, verts, faces, mat=None, parent=None):
    """
    Builds a new mesh object from vertices and faces, tags smooth shading,
    links it to the active collection, and assigns material/parent.
    """
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    for poly in mesh.polygons:
        poly.use_smooth = True

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    if mat is not None:
        obj.data.materials.append(mat)
    if parent is not None:
        obj.parent = parent

    return obj


def merge_mesh_data(verts1, faces1, verts2, faces2):
    """Merges two sets of vertices and faces into one unified mesh dataset."""
    offset = len(verts1)
    merged_verts = list(verts1) + list(verts2)
    merged_faces = list(faces1) + [[idx + offset for idx in f] for f in faces2]
    return merged_verts, merged_faces


# ---------------------------------------------------------------------------
# Procedural Geometry Generators
# ---------------------------------------------------------------------------
def build_revolved_mesh(
    profile,
    n_segments=24,
    cap_top=True,
    cap_bottom=True,
    petal_lobes=0,
    petal_amp=0.0,
    z_offset=0.0,
):
    """
    Revolves a 2D profile [(r, z), ...] around the Z-axis.
    Supports petal/fluting modulation on radius: r * (1 + amp * cos(lobes * theta)).
    """
    verts = []
    faces = []
    n_rings = len(profile)

    for i in range(n_rings):
        r_base, z = profile[i]
        for j in range(n_segments):
            theta = 2.0 * math.pi * j / n_segments
            r = r_base
            if petal_lobes > 0 and petal_amp != 0.0:
                r = r_base * (1.0 + petal_amp * math.cos(petal_lobes * theta))
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            verts.append((x, y, z + z_offset))

    for i in range(n_rings - 1):
        r_curr = i * n_segments
        r_next = (i + 1) * n_segments
        for j in range(n_segments):
            j_next = (j + 1) % n_segments
            v0 = r_curr + j
            v1 = r_curr + j_next
            v2 = r_next + j_next
            v3 = r_next + j
            faces.append((v0, v1, v2, v3))

    if cap_bottom and profile[0][0] > 1e-5:
        c_bot_idx = len(verts)
        verts.append((0.0, 0.0, profile[0][1] + z_offset))
        for j in range(n_segments):
            j_next = (j + 1) % n_segments
            faces.append((c_bot_idx, j_next, j))

    if cap_top and profile[-1][0] > 1e-5:
        c_top_idx = len(verts)
        verts.append((0.0, 0.0, profile[-1][1] + z_offset))
        r_top = (n_rings - 1) * n_segments
        for j in range(n_segments):
            j_next = (j + 1) % n_segments
            faces.append((c_top_idx, r_top + j, r_top + j_next))

    return verts, faces


def build_swept_tube(path_points, radius, n_circle=10, cap_ends=True):
    """
    Extrudes a cylindrical tube of uniform radius along a 3D path of points
    using parallel-transport reference frames to prevent twisting.
    """
    verts = []
    faces = []
    m = len(path_points)
    if m < 2:
        return verts, faces

    tangents = []
    for i in range(m):
        if i == 0:
            t = (path_points[1] - path_points[0]).normalized()
        elif i == m - 1:
            t = (path_points[-1] - path_points[-2]).normalized()
        else:
            t = (path_points[i + 1] - path_points[i - 1]).normalized()
        tangents.append(t)

    t0 = tangents[0]
    ref = mathutils.Vector((0.0, 0.0, 1.0))
    if abs(t0.dot(ref)) > 0.88:
        ref = mathutils.Vector((0.0, 1.0, 0.0))
    n0 = t0.cross(ref).normalized()
    b0 = t0.cross(n0).normalized()

    frames = [(n0, b0)]
    for i in range(1, m):
        t_prev = tangents[i - 1]
        t_curr = tangents[i]
        n_prev, b_prev = frames[-1]
        axis = t_prev.cross(t_curr)
        angle = t_prev.angle(t_curr, 0.0)
        if axis.length > 1e-6 and angle > 1e-6:
            rot = mathutils.Quaternion(axis, angle)
            n_curr = (rot @ n_prev).normalized()
            b_curr = (rot @ b_prev).normalized()
        else:
            n_curr = n_prev
            b_curr = b_prev
        frames.append((n_curr, b_curr))

    for i in range(m):
        p = path_points[i]
        n_vec, b_vec = frames[i]
        for j in range(n_circle):
            angle = 2.0 * math.pi * j / n_circle
            v = p + radius * (math.cos(angle) * n_vec + math.sin(angle) * b_vec)
            verts.append((v.x, v.y, v.z))

    for i in range(m - 1):
        r_curr = i * n_circle
        r_next = (i + 1) * n_circle
        for j in range(n_circle):
            j_next = (j + 1) % n_circle
            v0 = r_curr + j
            v1 = r_curr + j_next
            v2 = r_next + j_next
            v3 = r_next + j
            faces.append((v0, v1, v2, v3))

    if cap_ends:
        c_start_idx = len(verts)
        verts.append((path_points[0].x, path_points[0].y, path_points[0].z))
        for j in range(n_circle):
            j_next = (j + 1) % n_circle
            faces.append((c_start_idx, j_next, j))

        c_end_idx = len(verts)
        verts.append((path_points[-1].x, path_points[-1].y, path_points[-1].z))
        r_last = (m - 1) * n_circle
        for j in range(n_circle):
            j_next = (j + 1) % n_circle
            faces.append((c_end_idx, r_last + j, r_last + j_next))

    return verts, faces


def build_torus(
    r_major,
    r_minor,
    seg_major=24,
    seg_minor=12,
    center=mathutils.Vector((0.0, 0.0, 0.0)),
    axis="Z",
):
    """Builds a circular torus oriented around 'X', 'Y', or 'Z' axis."""
    verts = []
    faces = []
    for i in range(seg_major):
        phi = 2.0 * math.pi * i / seg_major
        cp = mathutils.Vector(
            (r_major * math.cos(phi), r_major * math.sin(phi), 0.0)
        )
        rad_dir = mathutils.Vector((math.cos(phi), math.sin(phi), 0.0))
        up_dir = mathutils.Vector((0.0, 0.0, 1.0))

        for j in range(seg_minor):
            theta = 2.0 * math.pi * j / seg_minor
            p = cp + r_minor * (
                math.cos(theta) * rad_dir + math.sin(theta) * up_dir
            )
            if axis == "X":
                p_rot = mathutils.Vector((p.z, p.y, -p.x))
            elif axis == "Y":
                p_rot = mathutils.Vector((p.x, p.z, -p.y))
            else:
                p_rot = p
            verts.append(
                (p_rot.x + center.x, p_rot.y + center.y, p_rot.z + center.z)
            )

    for i in range(seg_major):
        i_next = (i + 1) % seg_major
        for j in range(seg_minor):
            j_next = (j + 1) % seg_minor
            v0 = i * seg_minor + j
            v1 = i * seg_minor + j_next
            v2 = i_next * seg_minor + j_next
            v3 = i_next * seg_minor + j
            faces.append((v0, v1, v2, v3))

    return verts, faces


def build_sphere(
    radius, center=mathutils.Vector((0.0, 0.0, 0.0)), n_lat=8, n_lon=12
):
    """Builds a small UV sphere mesh (used for clapper pellets and decorative beads)."""
    profile = []
    for i in range(n_lat):
        phi = -0.5 * math.pi + math.pi * i / (n_lat - 1)
        r = radius * math.cos(phi)
        z = radius * math.sin(phi)
        profile.append((max(r, 1e-5), z))

    verts, faces = build_revolved_mesh(
        profile,
        n_segments=n_lon,
        cap_top=True,
        cap_bottom=True,
        z_offset=center.z,
    )
    shifted_verts = [(v[0] + center.x, v[1] + center.y, v[2]) for v in verts]
    return shifted_verts, faces


def build_suzu_bell(bell_radius):
    """
    Constructs an authentic Japanese Suzu (crotal bell) mesh:
    - Hollow resonance body with genuine wall thickness.
    - Prominent equatorial casting ridge / welt.
    - Hollow bottom acoustic mouth cavity.
    - Inner round clapper pellet.
    - Top arched suspension loop for mounting onto branch arm hooks.
    """
    r = bell_radius

    # Profile forming inner cavity ceiling, acoustic mouth rim, equator welt, and top neck
    profile = [
        (0.001 * r, -0.32 * r),
        (0.32 * r, -0.45 * r),
        (0.44 * r, -0.86 * r),  # Acoustic mouth rim
        (0.72 * r, -0.68 * r),
        (0.92 * r, -0.38 * r),
        (1.02 * r, -0.14 * r),
        (1.22 * r, 0.00 * r),  # Equatorial flange crest
        (1.02 * r, 0.14 * r),
        (0.94 * r, 0.40 * r),
        (0.75 * r, 0.68 * r),
        (0.48 * r, 0.86 * r),
        (0.26 * r, 0.98 * r),
        (0.22 * r, 1.08 * r),
        (0.001 * r, 1.10 * r),  # Top boss
    ]

    verts, faces = build_revolved_mesh(
        profile, n_segments=16, cap_top=True, cap_bottom=True
    )

    # Top suspension loop (half-circle tube arch in XZ plane)
    loop_pts = []
    n_loop_pts = 9
    loop_radius = 0.28 * r
    loop_base_z = 1.08 * r
    for i in range(n_loop_pts):
        ang = math.pi * i / (n_loop_pts - 1)
        lx = loop_radius * math.cos(ang)
        lz = loop_base_z + loop_radius * math.sin(ang)
        loop_pts.append(mathutils.Vector((lx, 0.0, lz)))

    loop_verts, loop_faces = build_swept_tube(
        loop_pts, radius=0.065 * r, n_circle=8, cap_ends=True
    )
    verts, faces = merge_mesh_data(verts, faces, loop_verts, loop_faces)

    # Inner round clapper pellet
    clapper_verts, clapper_faces = build_sphere(
        radius=0.18 * r,
        center=mathutils.Vector((0.0, 0.0, -0.52 * r)),
        n_lat=6,
        n_lon=10,
    )
    verts, faces = merge_mesh_data(verts, faces, clapper_verts, clapper_faces)

    return verts, faces


def build_ribbon(
    start_pos,
    spread_dir,
    phase,
    length=0.32,
    n_steps=24,
    width=0.016,
    thickness=0.0008,
):
    """
    Constructs a manifold, double-sided 3D silk streamer with realistic thickness,
    natural gravity drape, and gentle wave undulations.
    """
    verts = []
    faces = []

    pts = []
    for i in range(n_steps):
        t = i / (n_steps - 1)
        z = start_pos.z - t * length
        drift = 0.024 * (t**1.2)
        wave_a = 0.009 * math.sin(t * 3.4 * math.pi + phase)
        wave_b = 0.007 * math.cos(t * 2.6 * math.pi + phase * 0.8)
        x = start_pos.x + spread_dir.x * drift + wave_a
        y = start_pos.y + spread_dir.y * drift + wave_b
        pts.append(mathutils.Vector((x, y, z)))

    for i in range(n_steps):
        p = pts[i]
        t = i / (n_steps - 1)
        if i == 0:
            tang = (pts[1] - pts[0]).normalized()
        elif i == n_steps - 1:
            tang = (pts[-1] - pts[-2]).normalized()
        else:
            tang = (pts[i + 1] - pts[i - 1]).normalized()

        face_dir = mathutils.Vector(
            (-spread_dir.y, spread_dir.x, 0.0)
        ).normalized()
        w_vec = face_dir - tang * face_dir.dot(tang)
        if w_vec.length < 1e-4:
            w_vec = mathutils.Vector((1.0, 0.0, 0.0))
        else:
            w_vec = w_vec.normalized()

        n_vec = tang.cross(w_vec).normalized()
        hw = 0.5 * width * (1.0 - 0.15 * t)
        ht = 0.5 * thickness

        v0 = p + hw * w_vec + ht * n_vec
        v1 = p - hw * w_vec + ht * n_vec
        v2 = p - hw * w_vec - ht * n_vec
        v3 = p + hw * w_vec - ht * n_vec

        verts.extend(
            [
                (v0.x, v0.y, v0.z),
                (v1.x, v1.y, v1.z),
                (v2.x, v2.y, v2.z),
                (v3.x, v3.y, v3.z),
            ]
        )

    for i in range(n_steps - 1):
        r_c = i * 4
        r_n = (i + 1) * 4
        # Front face
        faces.append((r_c + 0, r_c + 1, r_n + 1, r_n + 0))
        # Right edge
        faces.append((r_c + 1, r_c + 2, r_n + 2, r_n + 1))
        # Back face
        faces.append((r_c + 2, r_c + 3, r_n + 3, r_n + 2))
        # Left edge
        faces.append((r_c + 3, r_c + 0, r_n + 0, r_n + 3))

    # Top and bottom caps
    faces.append((0, 3, 2, 1))
    last_r = (n_steps - 1) * 4
    faces.append((last_r + 0, last_r + 1, last_r + 2, last_r + 3))

    return verts, faces


# ---------------------------------------------------------------------------
# Main Model Assembly Entry Point
# ---------------------------------------------------------------------------
def build_model():
    """
    Constructs the complete Kagura Suzu 3D model near world origin with Z up.
    Creates editable geometry, distinct parts, and verified materials.
    """
    # 1. Create Materials with synchronized diffuse_color and Base Color
    mat_gold = create_material(
        "Kagura_Gold", COLOR_GOLD, metallic=0.92, roughness=0.18
    )
    mat_gold_dark = create_material(
        "Kagura_Gold_Dark", COLOR_GOLD_DARK, metallic=0.88, roughness=0.32
    )
    mat_lacquer_red = create_material(
        "Kagura_Lacquer_Red", COLOR_LACQUER_RED, metallic=0.04, roughness=0.12
    )
    mat_ivory = create_material(
        "Kagura_Ivory", COLOR_IVORY, metallic=0.0, roughness=0.32
    )
    mat_crimson_cord = create_material(
        "Kagura_Crimson_Cord", COLOR_CRIMSON_CORD, metallic=0.0, roughness=0.65
    )

    mat_rib_red = create_material(
        "Kagura_Ribbon_Red", COLOR_RIBBON_RED, metallic=0.0, roughness=0.45
    )
    mat_rib_white = create_material(
        "Kagura_Ribbon_White", COLOR_RIBBON_WHITE, metallic=0.0, roughness=0.45
    )
    mat_rib_yellow = create_material(
        "Kagura_Ribbon_Yellow", COLOR_RIBBON_YELLOW, metallic=0.0, roughness=0.45
    )
    mat_rib_green = create_material(
        "Kagura_Ribbon_Green", COLOR_RIBBON_GREEN, metallic=0.0, roughness=0.45
    )
    mat_rib_purple = create_material(
        "Kagura_Ribbon_Purple", COLOR_RIBBON_PURPLE, metallic=0.0, roughness=0.45
    )

    # 2. Lacquered Handle Sections (Vermilion Red Wood)
    # Lower wooden grip sleeve
    h_lower_v, h_lower_f = build_revolved_mesh(
        [(0.0125, -0.180), (0.0125, -0.140)],
        n_segments=24,
        cap_top=True,
        cap_bottom=True,
    )
    # Upper wooden grip sleeve
    h_upper_v, h_upper_f = build_revolved_mesh(
        [(0.0125, -0.040), (0.0125, 0.000)],
        n_segments=24,
        cap_top=True,
        cap_bottom=True,
    )
    grip_v, grip_f = merge_mesh_data(
        h_lower_v, h_lower_f, h_upper_v, h_upper_f
    )
    root_grip = create_mesh_object(
        "Handle_Lacquered_Grip", grip_v, grip_f, mat=mat_lacquer_red
    )

    # 3. Handle Ivory Wrap Core (shows through cord diamonds)
    ivory_v, ivory_f = build_revolved_mesh(
        [(0.0118, -0.140), (0.0118, -0.040)],
        n_segments=24,
        cap_top=True,
        cap_bottom=True,
    )
    create_mesh_object(
        "Handle_Ivory_Grip", ivory_v, ivory_f, mat=mat_ivory, parent=root_grip
    )

    # 4. Handle Braided Crimson Silk Cords (Tsuka-maki criss-cross binding)
    cord_v, cord_f = [], []
    n_helices = 4
    n_helix_steps = 32
    z_start = -0.140
    z_end = -0.040
    cord_rad = 0.0126
    wire_rad = 0.0011

    # Intersecting right-handed and left-handed helical strands
    for direction in [1.0, -1.0]:
        for k in range(n_helices):
            base_angle = 2.0 * math.pi * k / n_helices
            helix_pts = []
            for s in range(n_helix_steps):
                u = s / (n_helix_steps - 1)
                z = z_start + u * (z_end - z_start)
                ang = base_angle + direction * 1.25 * 2.0 * math.pi * u
                hx = cord_rad * math.cos(ang)
                hy = cord_rad * math.sin(ang)
                helix_pts.append(mathutils.Vector((hx, hy, z)))
            h_v, h_f = build_swept_tube(
                helix_pts, radius=wire_rad, n_circle=8, cap_ends=True
            )
            cord_v, cord_f = merge_mesh_data(cord_v, cord_f, h_v, h_f)

    # Border wrap rings at ends of ivory section
    for b_z in [-0.138, -0.042]:
        ring_v, ring_f = build_torus(
            r_major=0.0128,
            r_minor=0.0014,
            seg_major=24,
            seg_minor=10,
            center=mathutils.Vector((0.0, 0.0, b_z)),
            axis="Z",
        )
        cord_v, cord_f = merge_mesh_data(cord_v, cord_f, ring_v, ring_f)

    create_mesh_object(
        "Handle_Crimson_Cord_Wrap",
        cord_v,
        cord_f,
        mat=mat_crimson_cord,
        parent=root_grip,
    )

    # 5. Handle Golden Ferrules, End Cap & Mounting Eyelet
    ferrule_prof = [
        (0.0125, -0.180),
        (0.0138, -0.184),
        (0.0128, -0.190),
        (0.0100, -0.198),
        (0.0045, -0.202),
        (0.0001, -0.203),
    ]
    f_v, f_f = build_revolved_mesh(
        ferrule_prof, n_segments=24, cap_top=True, cap_bottom=True
    )

    # Spacer rings bordering the ivory section
    for s_z in [-0.140, -0.040]:
        s_v, s_f = build_torus(
            r_major=0.0130,
            r_minor=0.0012,
            seg_major=24,
            seg_minor=10,
            center=mathutils.Vector((0.0, 0.0, s_z)),
            axis="Z",
        )
        f_v, f_f = merge_mesh_data(f_v, f_f, s_v, s_f)

    # Bottom mounting eyelet
    eyelet_v, eyelet_f = build_torus(
        r_major=0.0055,
        r_minor=0.0013,
        seg_major=18,
        seg_minor=10,
        center=mathutils.Vector((0.0, 0.0, -0.209)),
        axis="Y",
    )
    f_v, f_f = merge_mesh_data(f_v, f_f, eyelet_v, eyelet_f)

    create_mesh_object(
        "Handle_Fittings_Gold", f_v, f_f, mat=mat_gold, parent=root_grip
    )

    # 6. Bottom Swivel Ring (interlinked through eyelet for ribbons)
    swivel_v, swivel_f = build_torus(
        r_major=0.0150,
        r_minor=0.0022,
        seg_major=24,
        seg_minor=12,
        center=mathutils.Vector((0.0, 0.0, -0.218)),
        axis="X",
    )
    create_mesh_object(
        "Bottom_Swivel_Ring", swivel_v, swivel_f, mat=mat_gold, parent=root_grip
    )

    # 7. Flared Lotus Guard (Tsuba) & Central Spindle Shaft
    lotus_prof = [
        (0.0125, 0.000),
        (0.0145, 0.004),
        (0.0195, 0.009),
        (0.0260, 0.016),
        (0.0285, 0.022),
        (0.0245, 0.024),
        (0.0120, 0.025),
        (0.0055, 0.026),
    ]
    tsuba_v, tsuba_f = build_revolved_mesh(
        lotus_prof,
        n_segments=32,
        cap_top=True,
        cap_bottom=True,
        petal_lobes=8,
        petal_amp=0.14,
    )

    # Stepped collar above guard
    collar_prof = [
        (0.0100, 0.026),
        (0.0112, 0.030),
        (0.0075, 0.034),
        (0.0048, 0.036),
    ]
    c_v, c_f = build_revolved_mesh(
        collar_prof, n_segments=24, cap_top=True, cap_bottom=True
    )
    tsuba_v, tsuba_f = merge_mesh_data(tsuba_v, tsuba_f, c_v, c_f)

    create_mesh_object(
        "Guard_Tsuba_Lotus", tsuba_v, tsuba_f, mat=mat_gold, parent=root_grip
    )

    # Central brass spindle rod and decorative spacer beads
    rod_prof = [(0.0045, 0.036), (0.0045, 0.190)]
    rod_v, rod_f = build_revolved_mesh(
        rod_prof, n_segments=16, cap_top=True, cap_bottom=True
    )

    # Spacer beads between tiers
    for sp_z in [0.095, 0.155]:
        sp_v, sp_f = build_sphere(
            radius=0.0075,
            center=mathutils.Vector((0.0, 0.0, sp_z)),
            n_lat=8,
            n_lon=14,
        )
        rod_v, rod_f = merge_mesh_data(rod_v, rod_f, sp_v, sp_f)

    create_mesh_object(
        "Central_Spindle_Shaft", rod_v, rod_f, mat=mat_gold, parent=root_grip
    )

    # 8. Top Finial (Giboshi / Sacred Flame Jewel)
    giboshi_prof = [
        (0.0055, 0.188),
        (0.0090, 0.191),
        (0.0062, 0.195),
        (0.0105, 0.200),
        (0.0135, 0.210),
        (0.0152, 0.222),  # Flame bulge
        (0.0125, 0.236),
        (0.0075, 0.246),
        (0.0028, 0.254),
        (0.0001, 0.258),  # Sharp peak
    ]
    finial_v, finial_f = build_revolved_mesh(
        giboshi_prof, n_segments=24, cap_top=True, cap_bottom=True
    )
    create_mesh_object(
        "Finial_Giboshi_Jewel",
        finial_v,
        finial_f,
        mat=mat_gold,
        parent=root_grip,
    )

    # -----------------------------------------------------------------------
    # 9. Three-Tiered Bell Armatures & Bells (Authentic 7 + 5 + 3 = 15 Bells)
    # -----------------------------------------------------------------------
    tier_specs = [
        {
            "name": "Tier1",
            "n_bells": 7,
            "z_hub": 0.065,
            "r_arm": 0.082,
            "bell_radius": 0.0160,
            "angle_offset": 0.0,
            "arm_rise": 0.008,
        },
        {
            "name": "Tier2",
            "n_bells": 5,
            "z_hub": 0.125,
            "r_arm": 0.062,
            "bell_radius": 0.0145,
            "angle_offset": math.pi / 5.0,
            "arm_rise": 0.007,
        },
        {
            "name": "Tier3",
            "n_bells": 3,
            "z_hub": 0.180,
            "r_arm": 0.044,
            "bell_radius": 0.0135,
            "angle_offset": math.pi / 3.0,
            "arm_rise": 0.006,
        },
    ]

    for tier in tier_specs:
        t_name = tier["name"]
        n_b = tier["n_bells"]
        z_h = tier["z_hub"]
        r_a = tier["r_arm"]
        b_rad = tier["bell_radius"]
        a_off = tier["angle_offset"]
        rise = tier["arm_rise"]

        arm_v, arm_f = [], []
        bell_v, bell_f = [], []

        # Central hub collar disc
        hub_prof = [
            (0.0048, z_h - 0.003),
            (0.0095, z_h - 0.003),
            (0.0095, z_h + 0.003),
            (0.0048, z_h + 0.003),
        ]
        h_v, h_f = build_revolved_mesh(
            hub_prof, n_segments=20, cap_top=True, cap_bottom=True
        )
        arm_v, arm_f = merge_mesh_data(arm_v, arm_f, h_v, h_f)

        # Single bell template mesh
        single_bell_v, single_bell_f = build_suzu_bell(b_rad)

        for i in range(n_b):
            theta = a_off + 2.0 * math.pi * i / n_b
            cos_t = math.cos(theta)
            sin_t = math.sin(theta)

            # Curved branch arm path
            arm_pts = []
            n_steps = 10
            for s in range(n_steps):
                u = s / (n_steps - 1)
                curr_r = 0.009 + (r_a - 0.009) * math.sin(u * 0.5 * math.pi)
                curr_z = z_h + rise * math.sin(u * math.pi) - 0.007 * (u**2)
                arm_pts.append(
                    mathutils.Vector((curr_r * cos_t, curr_r * sin_t, curr_z))
                )

            # Terminal downward hook at arm tip
            hook_tip_z = arm_pts[-1].z - 0.005
            hook_pts = [
                arm_pts[-1],
                mathutils.Vector(
                    ((r_a + 0.002) * cos_t, (r_a + 0.002) * sin_t, hook_tip_z)
                ),
                mathutils.Vector((r_a * cos_t, r_a * sin_t, hook_tip_z - 0.003)),
            ]
            arm_pts.extend(hook_pts[1:])

            tube_v, tube_f = build_swept_tube(
                arm_pts, radius=0.0016, n_circle=8, cap_ends=True
            )
            arm_v, arm_f = merge_mesh_data(arm_v, arm_f, tube_v, tube_f)

            # Position Suzu Bell directly hanging from hook
            bell_center_z = hook_tip_z - 0.003 - 1.36 * b_rad
            bell_center_x = r_a * cos_t
            bell_center_y = r_a * sin_t

            # Transform bell vertices to world branch location
            placed_bell_v = [
                (v[0] + bell_center_x, v[1] + bell_center_y, v[2] + bell_center_z)
                for v in single_bell_v
            ]
            bell_v, bell_f = merge_mesh_data(
                bell_v, bell_f, placed_bell_v, single_bell_f
            )

        # Create arm mesh object and bell mesh object for this tier
        create_mesh_object(
            f"{t_name}_Branch_Armature",
            arm_v,
            arm_f,
            mat=mat_gold_dark,
            parent=root_grip,
        )
        create_mesh_object(
            f"{t_name}_Suzu_Bells",
            bell_v,
            bell_f,
            mat=mat_gold,
            parent=root_grip,
        )

    # -----------------------------------------------------------------------
    # 10. Five-Color Sacred Streamers (Goshikio Ribbons)
    # -----------------------------------------------------------------------
    # Upper ribbon knot/collar binding right below the swivel ring
    knot_prof = [
        (0.0085, -0.222),
        (0.0115, -0.226),
        (0.0105, -0.234),
        (0.0075, -0.240),
    ]
    knot_v, knot_f = build_revolved_mesh(
        knot_prof, n_segments=20, cap_top=True, cap_bottom=True
    )
    create_mesh_object(
        "Ribbon_Top_Binding",
        knot_v,
        knot_f,
        mat=mat_crimson_cord,
        parent=root_grip,
    )

    ribbon_configs = [
        {
            "name": "Ribbon_Red",
            "mat": mat_rib_red,
            "angle": 0.0 * math.pi,
            "phase": 0.0,
        },
        {
            "name": "Ribbon_White",
            "mat": mat_rib_white,
            "angle": 0.4 * math.pi,
            "phase": 1.25,
        },
        {
            "name": "Ribbon_Yellow",
            "mat": mat_rib_yellow,
            "angle": 0.8 * math.pi,
            "phase": 2.50,
        },
        {
            "name": "Ribbon_Green",
            "mat": mat_rib_green,
            "angle": 1.2 * math.pi,
            "phase": 3.75,
        },
        {
            "name": "Ribbon_Purple",
            "mat": mat_rib_purple,
            "angle": 1.6 * math.pi,
            "phase": 5.00,
        },
    ]

    for rc in ribbon_configs:
        ang = rc["angle"]
        spread = mathutils.Vector((math.cos(ang), math.sin(ang), 0.0))
        r_start = mathutils.Vector(
            (0.008 * math.cos(ang), 0.008 * math.sin(ang), -0.238)
        )
        rib_v, rib_f = build_ribbon(
            start_pos=r_start,
            spread_dir=spread,
            phase=rc["phase"],
            length=0.34,
            n_steps=28,
            width=0.017,
            thickness=0.0008,
        )
        create_mesh_object(
            rc["name"], rib_v, rib_f, mat=rc["mat"], parent=root_grip
        )
