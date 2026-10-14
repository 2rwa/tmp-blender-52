"""
Procedural Mikoshi (Japanese Portable Shrine) 3D Model Generator
Compatible with Blender 5.2.2.
"""

import bpy
import math
from mathutils import Vector, Euler, Matrix


def create_material(name, base_color, metallic=0.0, roughness=0.4, clearcoat=0.0):
    """Create or reuse a Principled BSDF material compatible with Blender 5.2."""
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        # Blender 4.0+ / 5.x uses standard inputs
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = base_color
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Coat Weight" in bsdf.inputs:
            bsdf.inputs["Coat Weight"].default_value = clearcoat
        elif "Clearcoat" in bsdf.inputs:
            bsdf.inputs["Clearcoat"].default_value = clearcoat
    return mat


def create_mesh_object(name, verts, faces, mat=None, collection=None, parent=None):
    """Helper to create a mesh object from vertices and polygonal faces."""
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    obj = bpy.data.objects.new(name, mesh)
    if collection is None:
        collection = bpy.context.collection
    collection.objects.link(obj)
    
    if mat:
        obj.data.materials.append(mat)
    if parent is not None:
        obj.parent = parent
    return obj


def create_box(name, size, location=(0, 0, 0), rotation=(0, 0, 0), mat=None, parent=None):
    """Create an aligned 3D cuboid with explicit dimensions."""
    sx, sy, sz = size[0] / 2.0, size[1] / 2.0, size[2] / 2.0
    verts = [
        (-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz),
        (-sx, -sy,  sz), (sx, -sy,  sz), (sx, sy,  sz), (-sx, sy,  sz)
    ]
    faces = [
        (0, 1, 2, 3),  # Bottom
        (4, 7, 6, 5),  # Top
        (0, 4, 5, 1),  # Front
        (1, 5, 6, 2),  # Right
        (2, 6, 7, 3),  # Back
        (3, 7, 4, 0)   # Left
    ]
    obj = create_mesh_object(name, verts, faces, mat)
    obj.location = location
    obj.rotation_euler = rotation
    if parent:
        obj.parent = parent
    return obj


def create_cylinder(name, radius, depth, segments=16, location=(0, 0, 0), rotation=(0, 0, 0), mat=None, parent=None):
    """Create a procedural cylinder without relying on primitive operators."""
    verts = []
    half_d = depth / 2.0
    for i in range(segments):
        angle = 2.0 * math.pi * i / segments
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        verts.append((x, y, -half_d))
    for i in range(segments):
        angle = 2.0 * math.pi * i / segments
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        verts.append((x, y, half_d))

    faces = []
    # Bottom face
    faces.append([i for i in range(segments - 1, -1, -1)])
    # Top face
    faces.append([segments + i for i in range(segments)])
    # Side faces
    for i in range(segments):
        ni = (i + 1) % segments
        faces.append([i, ni, segments + ni, segments + i])

    obj = create_mesh_object(name, verts, faces, mat)
    obj.location = location
    obj.rotation_euler = rotation
    if parent:
        obj.parent = parent
    return obj


def create_cone(name, r_base, r_top, depth, segments=12, location=(0, 0, 0), rotation=(0, 0, 0), mat=None, parent=None):
    """Create a truncated or pointed procedural cone."""
    verts = []
    half_d = depth / 2.0
    for i in range(segments):
        ang = 2.0 * math.pi * i / segments
        verts.append((r_base * math.cos(ang), r_base * math.sin(ang), -half_d))
    for i in range(segments):
        ang = 2.0 * math.pi * i / segments
        verts.append((r_top * math.cos(ang), r_top * math.sin(ang), half_d))

    faces = []
    if r_base > 0.0001:
        faces.append([i for i in range(segments - 1, -1, -1)])
    if r_top > 0.0001:
        faces.append([segments + i for i in range(segments)])
    for i in range(segments):
        ni = (i + 1) % segments
        faces.append([i, ni, segments + ni, segments + i])

    obj = create_mesh_object(name, verts, faces, mat)
    obj.location = location
    obj.rotation_euler = rotation
    if parent:
        obj.parent = parent
    return obj


def build_nobe_bo_carrying_poles(materials, root):
    """Build the shoulder-carrying poles (Nagae / Nobe-bo) and lateral crossbars."""
    mat_wood = materials['lacquer_black']
    mat_gold = materials['gilt_brass']

    # Two main long beams (running in Y direction)
    spacing_x = 0.52
    length_y = 3.8
    beam_w = 0.09
    beam_h = 0.09
    pole_z = 0.50

    for side in (-1, 1):
        px = side * spacing_x
        # Main longitudinal beam
        create_box(
            f"Pole_Main_{'L' if side < 0 else 'R'}",
            (beam_w, length_y, beam_h),
            location=(px, 0.0, pole_z),
            mat=mat_wood,
            parent=root
        )
        # Gilt metal ornamental caps at each pole terminal
        cap_len = 0.14
        for y_end in (-1, 1):
            py = y_end * (length_y / 2.0 - cap_len / 2.0 + 0.005)
            create_box(
                f"Pole_EndCap_{side}_{y_end}",
                (beam_w + 0.012, cap_len, beam_h + 0.012),
                location=(px, py, pole_z),
                mat=mat_gold,
                parent=root
            )

    # Secondary wider outer helper poles (commonly used for 4-line shoulder carrying)
    outer_x = 0.88
    outer_len = 3.2
    for side in (-1, 1):
        px = side * outer_x
        create_box(
            f"Pole_Outer_{'L' if side < 0 else 'R'}",
            (beam_w * 0.9, outer_len, beam_h * 0.9),
            location=(px, 0.0, pole_z),
            mat=mat_wood,
            parent=root
        )
        cap_len = 0.12
        for y_end in (-1, 1):
            py = y_end * (outer_len / 2.0 - cap_len / 2.0 + 0.005)
            create_box(
                f"Pole_Outer_EndCap_{side}_{y_end}",
                (beam_w * 0.9 + 0.012, cap_len, beam_h * 0.9 + 0.012),
                location=(px, py, pole_z),
                mat=mat_gold,
                parent=root
            )

    # Transverse crossbeams (Yokobou) clamping the carrying poles
    cross_positions = [-1.1, -0.45, 0.45, 1.1]
    cross_w = 2.0
    for idx, cy in enumerate(cross_positions):
        create_box(
            f"CrossBeam_{idx}",
            (cross_w, 0.075, 0.075),
            location=(0.0, cy, pole_z + 0.08),
            mat=mat_wood,
            parent=root
        )
        # End caps on crossbars
        for end_x in (-1, 1):
            create_box(
                f"CrossBeam_Cap_{idx}_{end_x}",
                (0.06, 0.085, 0.085),
                location=(end_x * (cross_w / 2.0 - 0.03), cy, pole_z + 0.08),
                mat=mat_gold,
                parent=root
            )


def build_daiza_base(materials, root):
    """Build the tiered plinth/pedestal (Daiza) of the mikoshi."""
    mat_black = materials['lacquer_black']
    mat_red = materials['lacquer_vermilion']
    mat_gold = materials['gilt_brass']

    # Sub-base tiered pedestal blocks
    tier_specs = [
        ((1.30, 1.30, 0.07), 0.64, mat_black),
        ((1.22, 1.22, 0.06), 0.70, mat_red),
        ((1.14, 1.14, 0.08), 0.76, mat_black),
        ((1.08, 1.08, 0.05), 0.82, mat_gold),
        ((1.04, 1.04, 0.06), 0.87, mat_black),
    ]

    for idx, (sz, z_pos, mat) in enumerate(tier_specs):
        create_box(f"Base_Tier_{idx}", sz, location=(0.0, 0.0, z_pos), mat=mat, parent=root)

    # Engraved gilt corner corner-brackets (Kanamono) on the main base tiers
    for side_x in (-1, 1):
        for side_y in (-1, 1):
            cx = side_x * 0.58
            cy = side_y * 0.58
            create_box(
                f"Base_CornerFitting_{side_x}_{side_y}",
                (0.12, 0.12, 0.075),
                location=(cx, cy, 0.76),
                mat=mat_gold,
                parent=root
            )


def build_shrine_body_and_railings(materials, root):
    """Construct the main sanctum (Shinza/Torii-framed core), four main posts, and surrounding verandas/railings."""
    mat_black = materials['lacquer_black']
    mat_red = materials['lacquer_vermilion']
    mat_gold = materials['gilt_brass']
    mat_gold_leaf = materials['gold_leaf']

    # Sanctum core chamber
    body_w = 0.76
    body_h = 0.62
    body_z = 0.90 + body_h / 2.0
    create_box("Sanctum_Chamber", (body_w, body_w, body_h), location=(0.0, 0.0, body_z), mat=mat_black, parent=root)

    # 4 Main Upright Pillars (Hashira)
    pillar_dist = 0.40
    pillar_r = 0.038
    pillar_h = 0.68
    for sx in (-1, 1):
        for sy in (-1, 1):
            px, py = sx * pillar_dist, sy * pillar_dist
            # Round carved pillars
            create_cylinder(
                f"Main_Pillar_{sx}_{sy}",
                radius=pillar_r,
                depth=pillar_h,
                segments=16,
                location=(px, py, 0.90 + pillar_h / 2.0),
                mat=mat_red,
                parent=root
            )
            # Ornate gilt base-fittings (Habaki)
            create_cylinder(
                f"Pillar_BaseFitting_{sx}_{sy}",
                radius=pillar_r + 0.012,
                depth=0.07,
                segments=16,
                location=(px, py, 0.90 + 0.035),
                mat=mat_gold,
                parent=root
            )
            # Ornate gilt top collar fittings
            create_cylinder(
                f"Pillar_TopFitting_{sx}_{sy}",
                radius=pillar_r + 0.012,
                depth=0.07,
                segments=16,
                location=(px, py, 0.90 + pillar_h - 0.035),
                mat=mat_gold,
                parent=root
            )

    # Four side folding doors (Tobira) with decorative latticework & central brass plates
    for side, angle in [("Front", 0), ("Back", math.pi), ("Right", -math.pi / 2), ("Left", math.pi / 2)]:
        rot = (0, 0, angle)
        # Forward translation along local Y
        offset = Matrix.Rotation(angle, 4, 'Z') @ Vector((0, -body_w / 2.0 - 0.005, body_z))
        door = create_box(f"Door_Panel_{side}", (0.50, 0.02, body_h * 0.82), location=offset, rotation=rot, mat=mat_black, parent=root)
        # Gold latticework insert / center plate
        gold_offset = Matrix.Rotation(angle, 4, 'Z') @ Vector((0, -body_w / 2.0 - 0.012, body_z))
        create_box(f"Door_Ornament_{side}", (0.28, 0.012, body_h * 0.55), location=gold_offset, rotation=rot, mat=mat_gold_leaf, parent=root)
        # Lock clasp / handle fitting
        lock_offset = Matrix.Rotation(angle, 4, 'Z') @ Vector((0, -body_w / 2.0 - 0.022, body_z - 0.05))
        create_cylinder(f"Door_Lock_{side}", radius=0.025, depth=0.01, segments=12, location=lock_offset, rotation=(math.pi / 2, 0, angle), mat=mat_gold, parent=root)

    # Miniature Torii frames on the front and back of the sanctum
    for t_side, y_pos in [("Front", -0.47), ("Back", 0.47)]:
        for col_x in (-0.24, 0.24):
            create_cylinder(f"Torii_Post_{t_side}_{col_x}", 0.018, 0.52, segments=12, location=(col_x, y_pos, 1.15), mat=mat_red, parent=root)
        # Kasagi (top beam with subtle curve)
        create_box(f"Torii_Kasagi_{t_side}", (0.58, 0.036, 0.04), location=(0.0, y_pos, 1.42), mat=mat_black, parent=root)
        create_box(f"Torii_Shimaki_{t_side}", (0.54, 0.030, 0.025), location=(0.0, y_pos, 1.385), mat=mat_red, parent=root)
        create_box(f"Torii_Nuki_{t_side}", (0.51, 0.024, 0.026), location=(0.0, y_pos, 1.28), mat=mat_red, parent=root)
        create_box(f"Torii_Tablet_{t_side}", (0.07, 0.034, 0.08), location=(0.0, y_pos, 1.33), mat=mat_gold, parent=root)

    # Koran (Surrounding Balustrade & Veranda Railing)
    railing_dist = 0.51
    rail_post_h = 0.17
    rail_z = 0.90 + rail_post_h / 2.0

    # 4 Corner Giboshi Posts (with onion-shaped gilt Finials)
    for sx in (-1, 1):
        for sy in (-1, 1):
            px, py = sx * railing_dist, sy * railing_dist
            # Post
            create_box(f"Rail_CornerPost_{sx}_{sy}", (0.04, 0.04, rail_post_h), location=(px, py, rail_z), mat=mat_red, parent=root)
            # Giboshi ornament (base ring + dome + tip)
            create_cylinder(f"Giboshi_Ring_{sx}_{sy}", radius=0.028, depth=0.018, segments=12, location=(px, py, 0.90 + rail_post_h + 0.01), mat=mat_gold, parent=root)
            create_cone(f"Giboshi_Dome_{sx}_{sy}", r_base=0.026, r_top=0.002, depth=0.035, segments=12, location=(px, py, 0.90 + rail_post_h + 0.032), mat=mat_gold, parent=root)

    # Intermediate railing posts and horizontal bars (Sujikai / Kasagi)
    for sx in (-1, 1):
        # East/West side rails
        for seg in (-0.25, 0.0, 0.25):
            create_box(f"Rail_MidPost_EW_{sx}_{seg}", (0.03, 0.03, rail_post_h * 0.9), location=(sx * railing_dist, seg, rail_z - 0.01), mat=mat_red, parent=root)
            create_cylinder(f"Giboshi_Mid_EW_{sx}_{seg}", radius=0.02, depth=0.012, segments=10, location=(sx * railing_dist, seg, 0.90 + rail_post_h * 0.9 + 0.006), mat=mat_gold, parent=root)
            create_cone(f"Giboshi_Cone_EW_{sx}_{seg}", r_base=0.018, r_top=0.001, depth=0.024, segments=10, location=(sx * railing_dist, seg, 0.90 + rail_post_h * 0.9 + 0.02), mat=mat_gold, parent=root)
        # Rails
        create_box(f"Rail_Bar_Top_EW_{sx}", (0.028, 1.02, 0.022), location=(sx * railing_dist, 0.0, 0.90 + rail_post_h - 0.015), mat=mat_black, parent=root)
        create_box(f"Rail_Bar_Mid_EW_{sx}", (0.020, 1.02, 0.018), location=(sx * railing_dist, 0.0, 0.90 + rail_post_h * 0.5), mat=mat_red, parent=root)
        create_box(f"Rail_Bar_Bot_EW_{sx}", (0.025, 1.02, 0.020), location=(sx * railing_dist, 0.0, 0.90 + 0.02), mat=mat_black, parent=root)

    for sy in (-1, 1):
        # North/South side rails (leaving slight gap in middle for staircase/gateway)
        for offset_x in (-0.28, 0.28):
            create_box(f"Rail_MidPost_NS_{sy}_{offset_x}", (0.03, 0.03, rail_post_h * 0.9), location=(offset_x, sy * railing_dist, rail_z - 0.01), mat=mat_red, parent=root)
            create_cylinder(f"Giboshi_Mid_NS_{sy}_{offset_x}", radius=0.02, depth=0.012, segments=10, location=(offset_x, sy * railing_dist, 0.90 + rail_post_h * 0.9 + 0.006), mat=mat_gold, parent=root)
            create_cone(f"Giboshi_Cone_NS_{sy}_{offset_x}", r_base=0.018, r_top=0.001, depth=0.024, segments=10, location=(offset_x, sy * railing_dist, 0.90 + rail_post_h * 0.9 + 0.02), mat=mat_gold, parent=root)
        # Rail segments on either side of the entrance
        for seg_x in (-0.38, 0.38):
            create_box(f"Rail_Bar_Top_NS_{sy}_{seg_x}", (0.24, 0.028, 0.022), location=(seg_x, sy * railing_dist, 0.90 + rail_post_h - 0.015), mat=mat_black, parent=root)
            create_box(f"Rail_Bar_Mid_NS_{sy}_{seg_x}", (0.24, 0.020, 0.018), location=(seg_x, sy * railing_dist, 0.90 + rail_post_h * 0.5), mat=mat_red, parent=root)
            create_box(f"Rail_Bar_Bot_NS_{sy}_{seg_x}", (0.24, 0.025, 0.020), location=(seg_x, sy * railing_dist, 0.90 + 0.02), mat=mat_black, parent=root)

    # Stepped Entry Ramp / Stairs (Kaidan) on front & rear
    for sy in (-1, 1):
        stair_y_start = sy * (railing_dist + 0.03)
        for step in range(3):
            sw = 0.26
            sd = 0.06
            sh = 0.035
            sz_pos = 0.90 - (step + 1) * sh
            sy_pos = stair_y_start + sy * step * sd
            create_box(f"Stairs_{sy}_{step}", (sw, sd, sh), location=(0.0, sy_pos, sz_pos), mat=mat_black, parent=root)


def build_bracket_complex(materials, root):
    """Build the intricate Japanese bracket clusters (Kumimono / Doukyo) supporting the eaves."""
    mat_black = materials['lacquer_black']
    mat_red = materials['lacquer_vermilion']
    mat_gold = materials['gilt_brass']

    bracket_base_z = 1.52

    # Tier 1 brackets (Dai-to and Hijiki extending outward)
    for sx in (-1, 1):
        for sy in (-1, 1):
            px, py = sx * 0.40, sy * 0.40
            # Dai-to (large capital block)
            create_box(f"Daito_{sx}_{sy}", (0.11, 0.11, 0.045), location=(px, py, bracket_base_z), mat=mat_gold, parent=root)
            # Crossing bracket arms (Hijiki)
            create_box(f"Hijiki_X_{sx}_{sy}", (0.24, 0.06, 0.04), location=(px, py, bracket_base_z + 0.04), mat=mat_red, parent=root)
            create_box(f"Hijiki_Y_{sx}_{sy}", (0.06, 0.24, 0.04), location=(px, py, bracket_base_z + 0.04), mat=mat_red, parent=root)
            # Smaller bearing blocks (Maki-to) on bracket tips
            for bx in (-0.09, 0.09):
                create_box(f"Makito_X_{sx}_{sy}_{bx}", (0.045, 0.045, 0.03), location=(px + bx, py, bracket_base_z + 0.075), mat=mat_gold, parent=root)
            for by in (-0.09, 0.09):
                create_box(f"Makito_Y_{sx}_{sy}_{by}", (0.045, 0.045, 0.03), location=(px, py + by, bracket_base_z + 0.075), mat=mat_gold, parent=root)

    # Tier 2 cantilever beams (Maruki / Ootaru-ki) extending outward to eaves
    create_box("Eave_Coffer_Beam_1", (1.02, 1.02, 0.05), location=(0.0, 0.0, bracket_base_z + 0.09), mat=mat_black, parent=root)
    create_box("Eave_Coffer_Beam_2", (1.14, 1.14, 0.045), location=(0.0, 0.0, bracket_base_z + 0.13), mat=mat_red, parent=root)

    # Exposed rafter ends (Taruki) all along the underside
    rafter_count = 14
    rafter_span = 1.08
    spacing = rafter_span / (rafter_count - 1)
    for i in range(rafter_count):
        pos = -rafter_span / 2.0 + i * spacing
        # X direction rafters
        for ey in (-0.57, 0.57):
            create_box(f"Taruki_X_{i}_{ey}", (0.03, 0.08, 0.03), location=(pos, ey, bracket_base_z + 0.13), mat=mat_gold, parent=root)
        # Y direction rafters
        for ex in (-0.57, 0.57):
            create_box(f"Taruki_Y_{i}_{ex}", (0.08, 0.03, 0.03), location=(ex, pos, bracket_base_z + 0.13), mat=mat_gold, parent=root)


def build_tiered_shrine_roof(materials, root):
    """
    Build the iconic Japanese Mikoshi Nobe-hafu tiered roof.
    Features sweeping curved eaves (Sori), hip ridges, copper/black tiles,
    flanked gables (hafu), and ornate corner crests.
    """
    mat_black = materials['lacquer_black']
    mat_gold = materials['gilt_brass']
    mat_tile = materials['roof_black_tile']

    # Procedural swept roof shell (curved hip-and-gable eave flared outwards)
    # Generated via concentric rings with non-linear curvature
    z_start = 1.69
    num_rings = 7
    ring_specs = [
        # (width, height_offset, vertical_thickness)
        (1.58, 0.00, 0.055),  # Flared wide lower eave rim
        (1.48, 0.03, 0.050),
        (1.36, 0.07, 0.048),
        (1.22, 0.13, 0.048),
        (1.04, 0.21, 0.050),
        (0.84, 0.31, 0.055),
        (0.62, 0.43, 0.060),  # Upper roof platform
    ]

    for r_idx in range(num_rings - 1):
        w1, z1, th1 = ring_specs[r_idx]
        w2, z2, th2 = ring_specs[r_idx + 1]
        half1 = w1 / 2.0
        half2 = w2 / 2.0

        # Create lofted band quad mesh
        verts = [
            # Ring 1 outer
            (-half1, -half1, z_start + z1), (half1, -half1, z_start + z1),
            (half1,  half1, z_start + z1), (-half1,  half1, z_start + z1),
            # Ring 2 outer
            (-half2, -half2, z_start + z2), (half2, -half2, z_start + z2),
            (half2,  half2, z_start + z2), (-half2,  half2, z_start + z2),
            # Ring 1 inner / under
            (-half1 * 0.96, -half1 * 0.96, z_start + z1 - th1),
            ( half1 * 0.96, -half1 * 0.96, z_start + z1 - th1),
            ( half1 * 0.96,  half1 * 0.96, z_start + z1 - th1),
            (-half1 * 0.96,  half1 * 0.96, z_start + z1 - th1),
            # Ring 2 inner / under
            (-half2 * 0.96, -half2 * 0.96, z_start + z2 - th2),
            ( half2 * 0.96, -half2 * 0.96, z_start + z2 - th2),
            ( half2 * 0.96,  half2 * 0.96, z_start + z2 - th2),
            (-half2 * 0.96,  half2 * 0.96, z_start + z2 - th2),
        ]
        faces = [
            # Top surfaces
            (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
            # Bottom surfaces
            (12, 13, 9, 8), (13, 14, 10, 9), (14, 15, 11, 10), (15, 12, 8, 11),
        ]
        # Outer trim edge on lowest tier
        if r_idx == 0:
            faces.extend([(8, 9, 1, 0), (9, 10, 2, 1), (10, 11, 3, 2), (11, 8, 0, 3)])

        create_mesh_object(f"Roof_Slope_Band_{r_idx}", verts, faces, mat_tile, parent=root)

    # Heavy Gilt Eave Edging (Kizami / Karafukurin) along bottom perimeter
    edge_w = 1.60
    edge_z = z_start
    edge_th = 0.05
    for rot, name in [(0, "Front"), (math.pi, "Back"), (-math.pi / 2, "Right"), (math.pi / 2, "Left")]:
        offset = Matrix.Rotation(rot, 4, 'Z') @ Vector((0, -edge_w / 2.0, edge_z + 0.015))
        create_box(f"Roof_EdgeTrim_{name}", (edge_w + 0.05, edge_th, 0.04), location=offset, rotation=(0, 0, rot), mat=mat_gold, parent=root)

    # Four Swept Corner Hip Ridges (Kudarimune) reaching to the four corners
    for sx in (-1, 1):
        for sy in (-1, 1):
            ang = math.atan2(sy, sx)
            # Create angled ridge beam
            # End tip curls up subtly
            cx_mid, cy_mid = sx * 0.52, sy * 0.52
            cz_mid = z_start + 0.24
            # Ridge beam spanning diagonally
            ridge = create_box(
                f"Roof_Ridge_{sx}_{sy}",
                (0.08, 0.72, 0.06),
                location=(cx_mid, cy_mid, cz_mid),
                rotation=(-0.46 * sy, 0.46 * sx, ang + math.pi / 2),
                mat=mat_gold,
                parent=root
            )

            # Warabite (curled upward ornamental fern-scroll tip) at each roof corner
            tip_x, tip_y = sx * 0.81, sy * 0.81
            tip_z = z_start + 0.05
            # Curled scroll finial composed of sequential small segments
            scroll_pts = [
                (0.0, 0.0, 0.0),
                (sx * 0.04, sy * 0.04, 0.04),
                (sx * 0.06, sy * 0.06, 0.10),
                (sx * 0.05, sy * 0.05, 0.15),
                (sx * 0.01, sy * 0.01, 0.17),
                (-sx * 0.02, -sy * 0.02, 0.15),
            ]
            for s_idx in range(len(scroll_pts) - 1):
                p1 = scroll_pts[s_idx]
                p2 = scroll_pts[s_idx + 1]
                mid = (
                    tip_x + (p1[0] + p2[0]) / 2.0,
                    tip_y + (p1[1] + p2[1]) / 2.0,
                    tip_z + (p1[2] + p2[2]) / 2.0
                )
                dx, dy, dz = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
                seg_len = math.sqrt(dx*dx + dy*dy + dz*dz)
                create_box(
                    f"Warabite_{sx}_{sy}_{s_idx}",
                    (0.035, 0.035, seg_len),
                    location=mid,
                    rotation=(math.atan2(math.sqrt(dx*dx + dy*dy), dz), 0, math.atan2(dy, dx)),
                    mat=mat_gold,
                    parent=root
                )

    # Gable Pediments (Hafu - cusped ornamental gables on all 4 faces)
    for hafu_rot, h_side in [(0, "Front"), (math.pi, "Back"), (-math.pi / 2, "Right"), (math.pi / 2, "Left")]:
        h_offset = Matrix.Rotation(hafu_rot, 4, 'Z') @ Vector((0, -0.66, z_start + 0.18))
        # Left and right bargeboard wings forming gable peak
        wing_l = create_box(
            f"Hafu_Wing_L_{h_side}",
            (0.38, 0.03, 0.06),
            location=h_offset + Matrix.Rotation(hafu_rot, 4, 'Z') @ Vector((-0.14, 0.0, 0.05)),
            rotation=(0, 0.40, hafu_rot),
            mat=mat_gold,
            parent=root
        )
        wing_r = create_box(
            f"Hafu_Wing_R_{h_side}",
            (0.38, 0.03, 0.06),
            location=h_offset + Matrix.Rotation(hafu_rot, 4, 'Z') @ Vector((0.14, 0.0, 0.05)),
            rotation=(0, -0.40, hafu_rot),
            mat=mat_gold,
            parent=root
        )
        # Decorative suspended pendant (Gegyo) under gable apex
        gegyo_pos = h_offset + Matrix.Rotation(hafu_rot, 4, 'Z') @ Vector((0.0, -0.015, 0.03))
        create_cone(
            f"Gegyo_Pendant_{h_side}",
            r_base=0.06,
            r_top=0.01,
            depth=0.10,
            segments=10,
            location=gegyo_pos,
            rotation=(0, 0, hafu_rot),
            mat=mat_gold,
            parent=root
        )

    # Upper Roof Box / Ridge Block (Mune)
    create_box("Roof_Ridge_Base", (0.64, 0.64, 0.08), location=(0.0, 0.0, z_start + 0.46), mat=mat_black, parent=root)
    create_box("Roof_Ridge_Deck", (0.54, 0.54, 0.06), location=(0.0, 0.0, z_start + 0.52), mat=mat_gold, parent=root)
    create_box("Roof_Ridge_Plinth", (0.36, 0.36, 0.05), location=(0.0, 0.0, z_start + 0.57), mat=mat_black, parent=root)


def build_phoenix_crest(materials, root):
    """
    Construct the majestic golden Phoenix (Hou-ou) atop the mikoshi roof.
    Includes body, neck, head with crown crest, spread tiered wings, and flowing tail plumes.
    """
    mat_gold = materials['gilt_brass']
    mat_bright_gold = materials['gold_leaf']

    base_z = 2.31

    # Lotus pedestal (Rendai) supporting the phoenix
    create_cylinder("Phoenix_Pedestal_Stem", radius=0.11, depth=0.06, segments=16, location=(0.0, 0.0, base_z), mat=mat_gold, parent=root)
    create_cone("Phoenix_Lotus_Bowl", r_base=0.09, r_top=0.14, depth=0.07, segments=16, location=(0.0, 0.0, base_z + 0.05), mat=mat_gold, parent=root)

    # Stylized spherical jewel / orb (Hoju)
    create_cylinder("Phoenix_Orb", radius=0.085, depth=0.09, segments=16, location=(0.0, 0.0, base_z + 0.12), mat=mat_bright_gold, parent=root)

    # Phoenix Body Core
    body_z = base_z + 0.22
    create_cone("Phoenix_Torso", r_base=0.06, r_top=0.045, depth=0.14, segments=12, location=(0.0, 0.02, body_z), rotation=(0.35, 0, 0), mat=mat_bright_gold, parent=root)

    # Graceful arching Neck and Head (facing forward -Y)
    neck_segs = [
        ((0.0, -0.04, body_z + 0.07), (0.035, 0.035, 0.08), (0.6, 0, 0)),
        ((0.0, -0.09, body_z + 0.13), (0.028, 0.028, 0.07), (0.9, 0, 0)),
        ((0.0, -0.12, body_z + 0.18), (0.024, 0.024, 0.06), (1.3, 0, 0)),
    ]
    for n_idx, (n_loc, n_sz, n_rot) in enumerate(neck_segs):
        create_box(f"Phoenix_Neck_{n_idx}", n_sz, location=n_loc, rotation=n_rot, mat=mat_bright_gold, parent=root)

    # Phoenix Head
    head_loc = (0.0, -0.15, body_z + 0.21)
    create_box("Phoenix_Head", (0.045, 0.07, 0.045), location=head_loc, mat=mat_bright_gold, parent=root)
    # Sharp pointed Beak holding sacred bead
    create_cone("Phoenix_Beak", r_base=0.02, r_top=0.002, depth=0.05, segments=8, location=(0.0, -0.20, body_z + 0.20), rotation=(-math.pi / 2, 0, 0), mat=mat_gold, parent=root)
    # Crown crest feathers (Kanmuri)
    create_box("Phoenix_Crest_1", (0.012, 0.04, 0.09), location=(0.0, -0.15, body_z + 0.27), rotation=(-0.3, 0, 0), mat=mat_bright_gold, parent=root)
    create_box("Phoenix_Crest_2", (0.010, 0.03, 0.07), location=(0.0, -0.12, body_z + 0.26), rotation=(-0.6, 0, 0), mat=mat_bright_gold, parent=root)

    # Expansive Spread Wings (Tsubasa) on left and right sides
    for wing_side in (-1, 1):
        side_tag = "L" if wing_side < 0 else "R"
        # Primary, secondary, and tertiary feather sweeps
        feather_layers = [
            # (dx, dy, dz, length, roll_angle, pitch_angle)
            (0.12, 0.02, 0.04, 0.26, 0.35 * wing_side, -0.15),
            (0.20, 0.04, 0.10, 0.28, 0.55 * wing_side, -0.05),
            (0.28, 0.06, 0.16, 0.26, 0.80 * wing_side,  0.10),
            (0.33, 0.05, 0.22, 0.22, 1.10 * wing_side,  0.25),
        ]
        for f_idx, (fx, fy, fz, flen, f_roll, f_pitch) in enumerate(feather_layers):
            f_loc = (wing_side * fx, fy, body_z + fz)
            create_box(
                f"Phoenix_Wing_{side_tag}_{f_idx}",
                (flen, 0.035, 0.016),
                location=f_loc,
                rotation=(f_pitch, f_roll, wing_side * 0.2),
                mat=mat_bright_gold,
                parent=root
            )

    # Long Tail Plumes (Onagadori style triple streamer plumes)
    tail_streamers = [
        # (angle_y, spread_x, curl_offset_z)
        (0.0,   0.00, 0.38),
        (0.15, -0.08, 0.34),
        (0.15,  0.08, 0.34),
    ]
    for t_idx, (tilt_y, spread_x, t_len) in enumerate(tail_streamers):
        # Arc segment 1: upward back
        create_box(
            f"Phoenix_Tail_Seg1_{t_idx}",
            (0.025, 0.014, 0.20),
            location=(spread_x * 0.5, 0.12, body_z + 0.12),
            rotation=(0.7, tilt_y, 0),
            mat=mat_bright_gold,
            parent=root
        )
        # Arc segment 2: arching top
        create_box(
            f"Phoenix_Tail_Seg2_{t_idx}",
            (0.022, 0.012, 0.24),
            location=(spread_x * 0.9, 0.24, body_z + 0.22),
            rotation=(1.4, tilt_y, 0),
            mat=mat_bright_gold,
            parent=root
        )
        # Arc segment 3: cascading downward plume tip
        create_box(
            f"Phoenix_Tail_Seg3_{t_idx}",
            (0.020, 0.010, t_len),
            location=(spread_x * 1.3, 0.34, body_z + 0.14),
            rotation=(2.3, tilt_y, 0),
            mat=mat_gold,
            parent=root
        )


def build_cords_tassels_and_bells(materials, root):
    """
    Build silk cords (Agemaki knots), hanging vermilion/gold tassels (Fusa),
    and tiny hanging brass wind-bells (Suzu / Furin) under roof corners and posts.
    """
    mat_red_cord = materials['silk_vermilion']
    mat_gold_bell = materials['gilt_brass']
    mat_gold_leaf = materials['gold_leaf']

    # 1. Agemaki decorative cord knots and hanging tassels on the 4 shrine faces
    for face_rot, name in [(0, "Front"), (math.pi, "Back"), (-math.pi / 2, "Right"), (math.pi / 2, "Left")]:
        y_center = -0.42
        z_knot = 1.35
        base_vec = Matrix.Rotation(face_rot, 4, 'Z') @ Vector((0, y_center, z_knot))
        
        # Central bow loops of the Agemaki knot
        for side in (-1, 1):
            loop_pos = base_vec + Matrix.Rotation(face_rot, 4, 'Z') @ Vector((side * 0.05, -0.015, 0.02))
            create_cylinder(
                f"Agemaki_Loop_{name}_{side}",
                radius=0.035,
                depth=0.018,
                segments=12,
                location=loop_pos,
                rotation=(math.pi / 2, 0, face_rot),
                mat=mat_red_cord,
                parent=root
            )
        # Knot center core
        create_cylinder(
            f"Agemaki_Center_{name}",
            radius=0.025,
            depth=0.024,
            segments=12,
            location=base_vec + Matrix.Rotation(face_rot, 4, 'Z') @ Vector((0, -0.015, 0.0)),
            rotation=(math.pi / 2, 0, face_rot),
            mat=mat_gold_leaf,
            parent=root
        )
        # Two hanging cords descending to tassels
        for side in (-1, 1):
            cord_pos = base_vec + Matrix.Rotation(face_rot, 4, 'Z') @ Vector((side * 0.035, -0.018, -0.10))
            create_cylinder(
                f"Agemaki_Cord_{name}_{side}",
                radius=0.007,
                depth=0.18,
                segments=8,
                location=cord_pos,
                rotation=(0, 0, face_rot),
                mat=mat_red_cord,
                parent=root
            )
            # Tassel cap (golden cap)
            tassel_cap_pos = base_vec + Matrix.Rotation(face_rot, 4, 'Z') @ Vector((side * 0.035, -0.018, -0.20))
            create_cylinder(
                f"Tassel_Cap_{name}_{side}",
                radius=0.018,
                depth=0.022,
                segments=10,
                location=tassel_cap_pos,
                rotation=(0, 0, face_rot),
                mat=mat_gold_bell,
                parent=root
            )
            # Flared silk tassel skirt
            tassel_body_pos = base_vec + Matrix.Rotation(face_rot, 4, 'Z') @ Vector((side * 0.035, -0.018, -0.26))
            create_cone(
                f"Tassel_Body_{name}_{side}",
                r_base=0.016,
                r_top=0.028,
                depth=0.10,
                segments=12,
                location=tassel_body_pos,
                rotation=(0, 0, face_rot),
                mat=mat_red_cord,
                parent=root
            )

    # 2. Hanging Wind-Bells (Suzu) suspended from the four swept roof corners
    bell_z = 1.62
    for sx in (-1, 1):
        for sy in (-1, 1):
            bx = sx * 0.77
            by = sy * 0.77
            # Suspension cord
            create_cylinder(
                f"Bell_Cord_{sx}_{sy}",
                radius=0.004,
                depth=0.09,
                segments=6,
                location=(bx, by, bell_z + 0.045),
                mat=mat_red_cord,
                parent=root
            )
            # Little brass bell cup
            create_cone(
                f"Bell_Cup_{sx}_{sy}",
                r_base=0.010,
                r_top=0.025,
                depth=0.04,
                segments=12,
                location=(bx, by, bell_z - 0.015),
                mat=mat_gold_bell,
                parent=root
            )
            # Clapper sphere
            create_cylinder(
                f"Bell_Clapper_{sx}_{sy}",
                radius=0.008,
                depth=0.012,
                segments=8,
                location=(bx, by, bell_z - 0.038),
                mat=mat_gold_bell,
                parent=root
            )
            # Wind-catcher brass strip (Tanzaku) hanging below the bell
            create_box(
                f"Bell_Tanzaku_{sx}_{sy}",
                (0.018, 0.002, 0.08),
                location=(bx, by, bell_z - 0.085),
                rotation=(0, 0, 0.3 * sx),
                mat=mat_gold_bell,
                parent=root
            )

    # 3. Thick Ceremonial Ropes (Shimenawa style corner drape cords)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx = sx * 0.44
            cy = sy * 0.44
            # Vermilion/gold braided corner cord wraps on the main pillars
            for ring_i in range(3):
                create_cylinder(
                    f"Pillar_BraidRing_{sx}_{sy}_{ring_i}",
                    radius=0.046,
                    depth=0.015,
                    segments=12,
                    location=(cx, cy, 1.15 + ring_i * 0.04),
                    mat=mat_red_cord,
                    parent=root
                )


def build_model():
    """
    Main entry point. Creates the complete, standalone Japanese Mikoshi
    (portable hand-carried shrine) with all visible authentic components.
    """
    # Materials library for high contrast, authentic lacquer & gilding
    materials = {
        'lacquer_black': create_material("Urushi_Black", (0.02, 0.02, 0.022, 1.0), metallic=0.05, roughness=0.15, clearcoat=0.8),
        'lacquer_vermilion': create_material("Urushi_Shu_Red", (0.75, 0.04, 0.015, 1.0), metallic=0.02, roughness=0.22, clearcoat=0.6),
        'gilt_brass': create_material("Kanamono_Brass", (0.92, 0.72, 0.22, 1.0), metallic=0.92, roughness=0.25),
        'gold_leaf': create_material("Kinpaku_Gold", (1.0, 0.82, 0.18, 1.0), metallic=0.95, roughness=0.18),
        'roof_black_tile': create_material("Roof_Tile_Black", (0.04, 0.045, 0.05, 1.0), metallic=0.20, roughness=0.38),
        'silk_vermilion': create_material("Silk_Vermilion", (0.85, 0.05, 0.02, 1.0), metallic=0.0, roughness=0.65),
    }

    # Root empty to hold entire hierarchy cleanly at world origin
    root = bpy.data.objects.new("Japanese_Mikoshi", None)
    root.empty_display_type = 'ARROWS'
    root.empty_display_size = 0.5
    bpy.context.collection.objects.link(root)

    # 1. Carrying beams (Nagae / Nobe-bo hand poles, no wheels)
    build_nobe_bo_carrying_poles(materials, root)

    # 2. Tiered pedestal (Daiza plinth with brass corner plates)
    build_daiza_base(materials, root)

    # 3. Main body, 4 posts, torii accents, and veranda balustrade (Koran)
    build_shrine_body_and_railings(materials, root)

    # 4. Bracket complex (Kumimono & cantilever rafters)
    build_bracket_complex(materials, root)

    # 5. Tiered sweeping roof (Nobe-hafu gables, hip ridges, and Warabite)
    build_tiered_shrine_roof(materials, root)

    # 6. Phoenix crest (Hou-ou on lotus pedestal)
    build_phoenix_crest(materials, root)

    # 7. Silk tassels, Agemaki knots, and corner wind-bells
    build_cords_tassels_and_bells(materials, root)

    return root


if __name__ == "__main__":
    build_model()
