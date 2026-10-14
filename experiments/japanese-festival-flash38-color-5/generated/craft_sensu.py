"""
Japanese Folding Fan (Sensu) Procedural Generator for Blender 5.2.
Constructs an authentic fully-opened folding fan with pleated paper leaf,
geometric decorative panels (indigo, scarlet, ivory, gold), 18 bamboo ribs
(including outer guard ribs / oya-bone), pivot rivet (kaname), and trim.
"""

import math
import bpy
from mathutils import Matrix, Vector


def create_colored_material(name, rgba, roughness=0.4, metallic=0.0):
    """
    Creates a material ensuring both viewport diffuse_color (for Workbench)
    and Principled BSDF Base Color match explicitly.
    """
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)

    mat.use_nodes = True
    mat.diffuse_color = rgba

    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")

    if "Base Color" in bsdf.inputs:
        bsdf.inputs["Base Color"].default_value = rgba
    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = roughness
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = metallic

    return mat


def create_mesh_object(name, verts, faces, collection=None):
    """Helper to construct a Blender mesh and object from vertex and face lists."""
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=True)

    obj = bpy.data.objects.new(name, mesh)
    if collection is None:
        collection = bpy.context.scene.collection
    collection.objects.link(obj)
    return obj


def build_materials():
    """Generates the harmonious traditional Japanese color palette."""
    materials = {
        "indigo": create_colored_material(
            "Sensu_Indigo", (0.05, 0.12, 0.35, 1.0), roughness=0.55
        ),
        "scarlet": create_colored_material(
            "Sensu_Scarlet", (0.82, 0.10, 0.12, 1.0), roughness=0.50
        ),
        "ivory": create_colored_material(
            "Sensu_Ivory", (0.94, 0.92, 0.85, 1.0), roughness=0.60
        ),
        "gold": create_colored_material(
            "Sensu_GoldLeaf",
            (0.88, 0.72, 0.18, 1.0),
            roughness=0.25,
            metallic=0.85,
        ),
        "dark_edge": create_colored_material(
            "Sensu_DarkBorder", (0.10, 0.08, 0.08, 1.0), roughness=0.45
        ),
        "bamboo_inner": create_colored_material(
            "Sensu_BambooInner", (0.78, 0.65, 0.42, 1.0), roughness=0.35
        ),
        "bamboo_outer": create_colored_material(
            "Sensu_BambooLacquer",
            (0.24, 0.14, 0.08, 1.0),
            roughness=0.25,
        ),
        "brass_rivet": create_colored_material(
            "Sensu_KanameBrass",
            (0.85, 0.65, 0.15, 1.0),
            roughness=0.20,
            metallic=0.90,
        ),
    }
    return materials


def build_pleated_leaf(materials, config):
    """
    Builds the authentic zigzag pleated fan paper (Ougi-gami) with thickness,
    rib pockets, and divided geometric decorative panels.
    """
    num_folds = config["num_folds"]
    r_inner = config["leaf_inner_radius"]
    r_outer = config["leaf_outer_radius"]
    angle_start = config["angle_start"]
    angle_end = config["angle_end"]
    thickness = config["leaf_thickness"]
    amplitude = config["pleat_amplitude"]

    # Arc subdivisions along radius for geometric patterning (inner, mid, outer rings)
    r_rings = [
        r_inner,
        r_inner + 0.32 * (r_outer - r_inner),
        r_inner + 0.68 * (r_outer - r_inner),
        r_outer,
    ]
    num_r_steps = len(r_rings) - 1

    verts = []
    faces = []
    face_mat_indices = []

    # Two layers (front and back of paper) to give tangible thickness
    # Grid indexing: layer (0..1), ring (0..num_r_steps), fold (0..num_folds)
    for layer in range(2):
        z_offset = (layer - 0.5) * thickness
        for r_idx, r in enumerate(r_rings):
            # Pleat height scales slightly outward for natural fan geometry
            h_amp = amplitude * (0.4 + 0.6 * ((r - r_inner) / (r_outer - r_inner)))
            for f_idx in range(num_folds + 1):
                t = f_idx / num_folds
                theta = angle_start + t * (angle_end - angle_start)
                # Alternating pleat valley and crest
                pleat_z = (
                    h_amp if (f_idx % 2 == 1) else -h_amp
                ) + z_offset

                x = r * math.cos(theta)
                y = r * math.sin(theta)
                verts.append((x, y, pleat_z))

    ring_stride = num_folds + 1
    layer_stride = (num_r_steps + 1) * ring_stride

    def v_index(layer, r_i, f_i):
        return layer * layer_stride + r_i * ring_stride + f_i

    # Front faces (Layer 0)
    for r_i in range(num_r_steps):
        for f_i in range(num_folds):
            v0 = v_index(0, r_i, f_i)
            v1 = v_index(0, r_i, f_i + 1)
            v2 = v_index(0, r_i + 1, f_i + 1)
            v3 = v_index(0, r_i + 1, f_i)
            faces.append((v0, v1, v2, v3))

            # Geometric panel coloring (traditional Japanese diagonal block motifs)
            # 0: Indigo, 1: Scarlet, 2: Ivory, 3: Gold Leaf
            pattern_val = (f_i // 2 + r_i) % 4
            if pattern_val == 0:
                mat_idx = 0  # Indigo
            elif pattern_val == 1:
                mat_idx = 1  # Scarlet
            elif pattern_val == 2:
                mat_idx = 2  # Ivory
            else:
                mat_idx = 3  # Gold

            face_mat_indices.append(mat_idx)

    # Back faces (Layer 1) - flipped winding
    for r_i in range(num_r_steps):
        for f_i in range(num_folds):
            v0 = v_index(1, r_i, f_i)
            v1 = v_index(1, r_i + 1, f_i)
            v2 = v_index(1, r_i + 1, f_i + 1)
            v3 = v_index(1, r_i, f_i + 1)
            faces.append((v0, v1, v2, v3))
            face_mat_indices.append(2)  # Elegant ivory/washi backing

    # Edge side caps: Top rim, bottom rim, left edge, right edge
    # Outer circular edge (rim)
    for f_i in range(num_folds):
        top_front_0 = v_index(0, num_r_steps, f_i)
        top_front_1 = v_index(0, num_r_steps, f_i + 1)
        top_back_0 = v_index(1, num_r_steps, f_i)
        top_back_1 = v_index(1, num_r_steps, f_i + 1)
        faces.append((top_front_0, top_front_1, top_back_1, top_back_0))
        face_mat_indices.append(4)  # Dark border / edging

    # Inner circular edge
    for f_i in range(num_folds):
        bot_front_0 = v_index(0, 0, f_i)
        bot_front_1 = v_index(0, 0, f_i + 1)
        bot_back_0 = v_index(1, 0, f_i)
        bot_back_1 = v_index(1, 0, f_i + 1)
        faces.append((bot_front_0, bot_back_0, bot_back_1, bot_front_1))
        face_mat_indices.append(4)

    # Left & Right radial rim caps
    for r_i in range(num_r_steps):
        # Left edge (f_i = 0)
        lf_0 = v_index(0, r_i, 0)
        lf_1 = v_index(0, r_i + 1, 0)
        lb_0 = v_index(1, r_i, 0)
        lb_1 = v_index(1, r_i + 1, 0)
        faces.append((lf_0, lb_0, lb_1, lf_1))
        face_mat_indices.append(4)

        # Right edge (f_i = num_folds)
        rf_0 = v_index(0, r_i, num_folds)
        rf_1 = v_index(0, r_i + 1, num_folds)
        rb_0 = v_index(1, r_i, num_folds)
        rb_1 = v_index(1, r_i + 1, num_folds)
        faces.append((rf_0, rf_1, rb_1, rb_0))
        face_mat_indices.append(4)

    obj = create_mesh_object("Sensu_Leaf_Paper", verts, faces)

    # Slot in materials
    palette_keys = [
        materials["indigo"],
        materials["scarlet"],
        materials["ivory"],
        materials["gold"],
        materials["dark_edge"],
    ]
    for mat in palette_keys:
        obj.data.materials.append(mat)

    for p_idx, polygon in enumerate(obj.data.polygons):
        polygon.material_index = face_mat_indices[p_idx]

    return obj


def build_bamboo_rib(index, total_ribs, angle, config, materials):
    """
    Builds an individual carved bamboo rib radiating from the pivot point
    all the way to the fan rim. Distinguishes outer guard ribs (Oya-bone)
    with a lacquered profile from inner ribs (Naka-bone).
    """
    is_outer = (index == 0) or (index == total_ribs - 1)

    r_pivot = config["pivot_radius"]
    r_outer = config["leaf_outer_radius"] * (1.025 if is_outer else 0.995)
    width = config["guard_width"] if is_outer else config["rib_width"]
    thickness = (
        config["guard_thickness"] if is_outer else config["rib_thickness"]
    )
    pleat_z = (
        config["pleat_amplitude"] if (index % 2 == 1) else -config["pleat_amplitude"]
    )

    # Segments along the rib length: pivot hole, throat, paper base, and tip
    radii = [
        r_pivot * 0.7,
        r_pivot * 2.2,
        config["leaf_inner_radius"],
        r_outer * 0.7,
        r_outer,
    ]
    # Rib slightly tapers in width towards the upper tip
    w_factors = [1.2, 1.0, 0.9, 0.75, 0.6]

    verts = []
    faces = []

    # Build tapered box along local radial axis
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    # Unit normal vector perpendicular to radial direction in XY plane
    nx = -sin_a
    ny = cos_a

    num_pts = len(radii)
    # 4 vertices per section (bottom-left, bottom-right, top-right, top-left)
    for i, r in enumerate(radii):
        w = (width * 0.5) * w_factors[i]
        # Blend z elevation from pivot plane (z=0) to the pleat fold plane
        blend = min(
            1.0, max(0.0, (r - r_pivot * 2.0) / (config["leaf_inner_radius"]))
        )
        z_mid = pleat_z * blend
        z_lo = z_mid - thickness * 0.5
        z_hi = z_mid + thickness * 0.5

        cx = r * cos_a
        cy = r * sin_a

        v_bl = (cx - nx * w, cy - ny * w, z_lo)
        v_br = (cx + nx * w, cy + ny * w, z_lo)
        v_tr = (cx + nx * w, cy + ny * w, z_hi)
        v_tl = (cx - nx * w, cy - ny * w, z_hi)

        verts.extend([v_bl, v_br, v_tr, v_tl])

    # Connect segments
    for i in range(num_pts - 1):
        b = i * 4
        nb = (i + 1) * 4
        # Bottom face
        faces.append((b + 0, nb + 0, nb + 1, b + 1))
        # Top face
        faces.append((b + 3, b + 2, nb + 2, nb + 3))
        # Left side
        faces.append((b + 0, b + 3, nb + 3, nb + 0))
        # Right side
        faces.append((b + 1, nb + 1, nb + 2, b + 2))

    # Bottom end cap
    faces.append((0, 1, 2, 3))
    # Top tip cap
    last = (num_pts - 1) * 4
    faces.append((last + 3, last + 2, last + 1, last + 0))

    name = f"Sensu_GuardRib_{index}" if is_outer else f"Sensu_InnerRib_{index}"
    obj = create_mesh_object(name, verts, faces)

    mat = materials["bamboo_outer"] if is_outer else materials["bamboo_inner"]
    obj.data.materials.append(mat)
    return obj


def build_pivot_rivet(config, materials):
    """
    Constructs the brass pivot pin / rivet (Kaname) holding the ribs
    together at the apex of the fan, complete with dual end heads and washer.
    """
    verts = []
    faces = []

    segments = 16
    pin_radius = config["pivot_radius"] * 0.35
    head_radius = config["pivot_radius"] * 0.85
    total_len = (
        config["guard_thickness"] * 2.8 + config["rib_thickness"] * 1.5
    )
    half_len = total_len * 0.5

    # Cylinder body for the pin
    # Ring 0: bottom, Ring 1: top
    for i in range(segments):
        theta = (2.0 * math.pi * i) / segments
        cx = pin_radius * math.cos(theta)
        cy = pin_radius * math.sin(theta)
        verts.append((cx, cy, -half_len))
        verts.append((cx, cy, half_len))

    for i in range(segments):
        next_i = (i + 1) % segments
        v0 = i * 2
        v1 = v0 + 1
        v2 = next_i * 2 + 1
        v3 = next_i * 2
        faces.append((v0, v3, v2, v1))

    # Top and bottom domed ornamental rivet heads (Kaname washers)
    head_offset = len(verts)

    def add_dome_head(z_pos, sign):
        start_v = len(verts)
        # Center peak
        verts.append((0.0, 0.0, z_pos + sign * 0.003))
        # Outer ring
        for i in range(segments):
            theta = (2.0 * math.pi * i) / segments
            cx = head_radius * math.cos(theta)
            cy = head_radius * math.sin(theta)
            verts.append((cx, cy, z_pos))
        for i in range(segments):
            ni = (i + 1) % segments
            if sign > 0:
                faces.append((start_v, start_v + 1 + i, start_v + 1 + ni))
            else:
                faces.append((start_v, start_v + 1 + ni, start_v + 1 + i))

    add_dome_head(half_len, 1.0)
    add_dome_head(-half_len, -1.0)

    obj = create_mesh_object("Sensu_Pivot_Kaname", verts, faces)
    obj.data.materials.append(materials["brass_rivet"])
    return obj


def build_hanging_knot(config, materials):
    """
    Creates an ornamental silk cord ring and knot loop dangling from the rivet,
    a characteristic feature of formal ceremonial Japanese folding fans.
    """
    verts = []
    faces = []

    ring_r = config["pivot_radius"] * 0.95
    tube_r = 0.0018
    r_segs = 16
    c_segs = 8

    # Torus centered below pivot
    z_center = -config["guard_thickness"] * 2.5
    y_center = -config["pivot_radius"] * 0.5

    for i in range(r_segs):
        theta = 2.0 * math.pi * i / r_segs
        for j in range(c_segs):
            phi = 2.0 * math.pi * j / c_segs
            x = (ring_r + tube_r * math.cos(phi)) * math.cos(theta)
            y = (
                y_center
                + (ring_r + tube_r * math.cos(phi)) * math.sin(theta) * 0.8
            )
            z = z_center + tube_r * math.sin(phi)
            verts.append((x, y, z))

    for i in range(r_segs):
        ni = (i + 1) % r_segs
        for j in range(c_segs):
            nj = (j + 1) % c_segs
            v0 = i * c_segs + j
            v1 = ni * c_segs + j
            v2 = ni * c_segs + nj
            v3 = i * c_segs + nj
            faces.append((v0, v1, v2, v3))

    obj = create_mesh_object("Sensu_SilkCord_TasselLoop", verts, faces)
    obj.data.materials.append(materials["scarlet"])
    return obj


def build_fan_display_stand(materials):
    """
    Builds a traditional dark lacquered wooden fan display stand (Sensu-kake)
    positioned under the fan to give it museum-grade grounding and presentation.
    """
    base_w = 0.32
    base_d = 0.09
    base_h = 0.014

    verts = [
        (-base_w * 0.5, -base_d * 0.5, -0.05),
        (base_w * 0.5, -base_d * 0.5, -0.05),
        (base_w * 0.5, base_d * 0.5, -0.05),
        (-base_w * 0.5, base_d * 0.5, -0.05),
        (-base_w * 0.48, -base_d * 0.46, -0.05 + base_h),
        (base_w * 0.48, -base_d * 0.46, -0.05 + base_h),
        (base_w * 0.48, base_d * 0.46, -0.05 + base_h),
        (-base_w * 0.48, base_d * 0.46, -0.05 + base_h),
    ]

    faces = [
        (0, 1, 2, 3),  # bottom
        (7, 6, 5, 4),  # top
        (0, 4, 5, 1),  # front
        (1, 5, 6, 2),  # right
        (2, 6, 7, 3),  # back
        (3, 7, 4, 0),  # left
    ]

    # Two small slotted upright pegs to cradle the fan
    peg_offset = 0.075
    peg_w = 0.012
    peg_d = 0.018
    peg_h = 0.045
    z_base = -0.05 + base_h

    for side in (-1, 1):
        start_idx = len(verts)
        px = side * peg_offset
        v_peg = [
            (px - peg_w * 0.5, -peg_d * 0.5, z_base),
            (px + peg_w * 0.5, -peg_d * 0.5, z_base),
            (px + peg_w * 0.5, peg_d * 0.5, z_base),
            (px - peg_w * 0.5, peg_d * 0.5, z_base),
            (px - peg_w * 0.5, -peg_d * 0.5, z_base + peg_h),
            (px + peg_w * 0.5, -peg_d * 0.5, z_base + peg_h),
            (px + peg_w * 0.5, peg_d * 0.5, z_base + peg_h),
            (px - peg_w * 0.5, peg_d * 0.5, z_base + peg_h),
        ]
        verts.extend(v_peg)
        faces.extend(
            [
                (start_idx + 7, start_idx + 6, start_idx + 5, start_idx + 4),
                (start_idx + 0, start_idx + 4, start_idx + 5, start_idx + 1),
                (start_idx + 1, start_idx + 5, start_idx + 6, start_idx + 2),
                (start_idx + 2, start_idx + 6, start_idx + 7, start_idx + 3),
                (start_idx + 3, start_idx + 7, start_idx + 4, start_idx + 0),
            ]
        )

    obj = create_mesh_object("Sensu_DisplayStand", verts, faces)
    obj.data.materials.append(materials["bamboo_outer"])
    return obj


def build_model():
    """
    Main entry point for building the Japanese folding fan (Sensu).
    Creates all fan components, organizes parent hierarchy, and positions
    the model at world origin.
    """
    # Authentic sensu proportions (approx 28cm opened fan)
    config = {
        "num_folds": 28,  # Pleats in paper leaf
        "num_ribs": 18,  # Distinct bamboo ribs (16 inner + 2 outer guards)
        "angle_start": math.radians(22.0),
        "angle_end": math.radians(158.0),
        "leaf_inner_radius": 0.125,
        "leaf_outer_radius": 0.285,
        "leaf_thickness": 0.0016,
        "pleat_amplitude": 0.0095,
        "pivot_radius": 0.012,
        "rib_width": 0.006,
        "rib_thickness": 0.003,
        "guard_width": 0.011,
        "guard_thickness": 0.006,
    }

    materials = build_materials()

    # 1. Pleated paper leaf (Ougi-gami) with geometric color fields
    leaf_obj = build_pleated_leaf(materials, config)

    # 2. Bamboo ribs (Hone)
    total_ribs = config["num_ribs"]
    start_ang = config["angle_start"]
    end_ang = config["angle_end"]
    rib_objs = []
    for i in range(total_ribs):
        t = i / (total_ribs - 1)
        ang = start_ang + t * (end_ang - start_ang)
        rib = build_bamboo_rib(i, total_ribs, ang, config, materials)
        rib_objs.append(rib)

    # 3. Pivot rivet (Kaname)
    rivet_obj = build_pivot_rivet(config, materials)

    # 4. Silk knot cord loop
    loop_obj = build_hanging_knot(config, materials)

    # 5. Traditional wooden display stand
    stand_obj = build_fan_display_stand(materials)

    # Hierarchy: Create a fan root empty at origin and parent movable parts
    root_obj = bpy.data.objects.new("Sensu_Fan_Assembly", None)
    bpy.context.scene.collection.objects.link(root_obj)
    root_obj.location = (0.0, 0.0, 0.0)

    # Tilt fan slightly backward into stand cradle for a realistic resting angle
    fan_components = [leaf_obj, rivet_obj, loop_obj] + rib_objs
    tilt_angle = math.radians(12.0)
    rot_matrix = Matrix.Rotation(tilt_angle, 4, "X")

    for obj in fan_components:
        obj.parent = root_obj
        obj.matrix_world = rot_matrix @ obj.matrix_world

    stand_obj.parent = root_obj

    return root_obj
