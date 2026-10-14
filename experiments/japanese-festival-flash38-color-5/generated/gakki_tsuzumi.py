"""
Procedural 3D Model of a Japanese Tsuzumi Hand Drum for Blender 5.2.
Created as a standalone script defining build_model().
"""

import bpy
import math
from mathutils import Vector, Matrix


def create_material(name, color_rgba, roughness=0.3, metallic=0.0):
    """Creates a Principled BSDF material and sets both viewport diffuse_color and shader base color."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.diffuse_color = color_rgba

    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color_rgba
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
    return mat


def create_mesh_object(name, verts, faces, material=None, parent=None):
    """Utility to create a mesh object from vertices and faces, link to scene, and set parent."""
    mesh = bpy.data.meshes.new(name=name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name=name, object_data=mesh)
    bpy.context.scene.collection.objects.link(obj)

    if material:
        obj.data.materials.append(material)

    if parent:
        obj.parent = parent

    return obj


def build_revolved_mesh(name, profile_points, segments=32, material=None, parent=None):
    """Revolves a 2D profile (r, z) around the Z axis to create a solid rotational mesh."""
    verts = []
    faces = []
    n_prof = len(profile_points)

    for seg in range(segments):
        theta = 2.0 * math.pi * seg / segments
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        for r, z in profile_points:
            verts.append((r * cos_t, r * sin_t, z))

    for seg in range(segments):
        next_seg = (seg + 1) % segments
        col1 = seg * n_prof
        col2 = next_seg * n_prof
        for i in range(n_prof - 1):
            p1 = col1 + i
            p2 = col1 + i + 1
            p3 = col2 + i + 1
            p4 = col2 + i
            faces.append((p1, p2, p3, p4))

    return create_mesh_object(name, verts, faces, material=material, parent=parent)


def build_cylinder(name, radius, height, segments=24, z_offset=0.0, material=None, parent=None):
    """Builds a closed vertical cylinder mesh."""
    profile = [
        (0.0, -height * 0.5 + z_offset),
        (radius, -height * 0.5 + z_offset),
        (radius, height * 0.5 + z_offset),
        (0.0, height * 0.5 + z_offset),
    ]
    return build_revolved_mesh(name, profile, segments=segments, material=material, parent=parent)


def build_tube_along_points(name, points, radius=0.012, segments=8, material=None, parent=None):
    """Builds a continuous polygonal tube following a sequence of 3D points."""
    if len(points) < 2:
        return None

    verts = []
    faces = []

    def get_ring_basis(tangent, approx_up=Vector((0.0, 0.0, 1.0))):
        tangent = tangent.normalized()
        if abs(tangent.dot(approx_up)) > 0.95:
            approx_up = Vector((0.0, 1.0, 0.0))
        side = tangent.cross(approx_up).normalized()
        up = side.cross(tangent).normalized()
        return side, up

    last_ring_start = None
    for i, p in enumerate(points):
        if i == 0:
            tangent = points[1] - points[0]
        elif i == len(points) - 1:
            tangent = points[-1] - points[-2]
        else:
            tangent = (points[i + 1] - points[i - 1]).normalized()

        side, up = get_ring_basis(tangent)
        ring_start = len(verts)

        for s in range(segments):
            angle = 2.0 * math.pi * s / segments
            offset = side * (math.cos(angle) * radius) + up * (math.sin(angle) * radius)
            v = p + offset
            verts.append((v.x, v.y, v.z))

        if last_ring_start is not None:
            for s in range(segments):
                next_s = (s + 1) % segments
                v1 = last_ring_start + s
                v2 = last_ring_start + next_s
                v3 = ring_start + next_s
                v4 = ring_start + s
                faces.append((v1, v2, v3, v4))

        last_ring_start = ring_start

    # Caps
    start_center = len(verts)
    verts.append((points[0].x, points[0].y, points[0].z))
    for s in range(segments):
        faces.append((start_center, (s + 1) % segments, s))

    end_center = len(verts)
    verts.append((points[-1].x, points[-1].y, points[-1].z))
    end_ring_start = last_ring_start
    for s in range(segments):
        faces.append((end_center, end_ring_start + s, end_ring_start + (s + 1) % segments))

    return create_mesh_object(name, verts, faces, material=material, parent=parent)


def build_model():
    """Main entry point to procedurally build the Japanese Tsuzumi hand drum."""
    # Root drum container
    root = bpy.data.objects.new("Japanese_Tsuzumi", None)
    bpy.context.scene.collection.objects.link(root)

    # ----------------------------------------------------
    # Materials with matching Diffuse and Principled BSDF
    # ----------------------------------------------------
    # 1. Vermilion / Japanese Cinnabar Lacquer (Shu-nuri)
    mat_lacquer = create_material("Mat_Vermilion_Lacquer", (0.85, 0.16, 0.08, 1.0), roughness=0.18, metallic=0.0)
    # 2. Aged Ivory Drumhead Skin (Kawa / Parchment)
    mat_membrane = create_material("Mat_Ivory_Skin", (0.92, 0.88, 0.76, 1.0), roughness=0.65, metallic=0.0)
    # 3. Outer Curved Lacquered Black Rims (Taiko Waku)
    mat_rim = create_material("Mat_Black_Rim", (0.05, 0.05, 0.06, 1.0), roughness=0.25, metallic=0.0)
    # 4. Rich Gold Leaf / Gilded Brass Fittings (Kande / Choshitsu)
    mat_gold = create_material("Mat_Gilded_Brass", (0.95, 0.72, 0.15, 1.0), roughness=0.28, metallic=0.85)
    # 5. Crimson Orange Main Tension Cord (Tate-o)
    mat_tate_o = create_material("Mat_Orange_Cord", (0.92, 0.32, 0.08, 1.0), roughness=0.75, metallic=0.0)
    # 6. Deep Dark Indigo/Black Center Tuning Cord (Momi-o / Uchi-shirabe)
    mat_momi_o = create_material("Mat_Indigo_Cord", (0.08, 0.09, 0.14, 1.0), roughness=0.7, metallic=0.0)
    # 7. Decorative Silk Cord Accent / Tassel (Kazari-himo)
    mat_purple_silk = create_material("Mat_Purple_Silk", (0.42, 0.12, 0.52, 1.0), roughness=0.5, metallic=0.0)

    # ----------------------------------------------------
    # 1. Hourglass Wooden Body (Dou / 胴)
    # ----------------------------------------------------
    # Profile: (radius, z) defining the classic curved flare and internal chamber
    # Tsuzumi total body height is ~25cm, waist radius ~4.2cm, bell ends ~10.5cm
    body_profile = [
        # Inner cavity wall
        (0.025, 0.0),
        (0.040, 0.05),
        (0.065, 0.10),
        (0.082, 0.13),
        # Outer rim lip and steps
        (0.098, 0.13),
        (0.106, 0.126),
        (0.108, 0.118),
        # Outer hourglass curve going towards waist
        (0.096, 0.095),
        (0.082, 0.075),
        (0.068, 0.055),
        (0.054, 0.035),
        (0.045, 0.018),
        # Central ring ribs at the waist (Nodowa)
        (0.048, 0.010),
        (0.043, 0.005),
        (0.048, 0.000),
        (0.043, -0.005),
        (0.048, -0.010),
        # Lower hourglass curve
        (0.045, -0.018),
        (0.054, -0.035),
        (0.068, -0.055),
        (0.082, -0.075),
        (0.096, -0.095),
        # Lower rim lip
        (0.108, -0.118),
        (0.106, -0.126),
        (0.098, -0.13),
        # Lower inner cavity wall
        (0.082, -0.13),
        (0.065, -0.10),
        (0.040, -0.05),
        (0.025, 0.0),
    ]
    build_revolved_mesh("Tsuzumi_Body_Dou", body_profile, segments=48, material=mat_lacquer, parent=root)

    # Gold decorative inlay bands near the flares (Maki-e style rings)
    gold_band_top = [
        (0.087, 0.082),
        (0.089, 0.082),
        (0.089, 0.088),
        (0.087, 0.088),
    ]
    build_revolved_mesh("Gold_Band_Top", gold_band_top, segments=36, material=mat_gold, parent=root)

    gold_band_bot = [
        (0.087, -0.088),
        (0.089, -0.088),
        (0.089, -0.082),
        (0.087, -0.082),
    ]
    build_revolved_mesh("Gold_Band_Bottom", gold_band_bot, segments=36, material=mat_gold, parent=root)

    # ----------------------------------------------------
    # 2. Drumheads: Ivory Membranes & Black Lacquered Rims (Kawa / 革)
    # ----------------------------------------------------
    # The two drumheads (front / rear) exceed the body diameter, mounted on thick stitched rims
    rim_outer_r = 0.145
    rim_inner_r = 0.105
    rim_thickness = 0.022
    membrane_r = 0.105

    for sign, suffix in [(1, "Top"), (-1, "Bottom")]:
        z_pos = sign * 0.138

        # Ivory parchment membrane face (convex curved drum head)
        memb_profile = [
            (0.0, z_pos + sign * 0.005),
            (membrane_r * 0.5, z_pos + sign * 0.003),
            (membrane_r * 0.85, z_pos + sign * 0.001),
            (membrane_r, z_pos),
            (membrane_r, z_pos - sign * 0.004),
            (0.0, z_pos - sign * 0.004),
        ]
        build_revolved_mesh(f"Membrane_{suffix}", memb_profile, segments=40, material=mat_membrane, parent=root)

        # Central striking spot reinforcement (Mitsudomoe / Keshou-gami circular target)
        patch_profile = [
            (0.0, z_pos + sign * 0.0065),
            (0.038, z_pos + sign * 0.0062),
            (0.038, z_pos + sign * 0.0052),
            (0.0, z_pos + sign * 0.0052),
        ]
        build_revolved_mesh(f"Strike_Patch_{suffix}", patch_profile, segments=24, material=mat_gold, parent=root)

        # Heavy circular outer rim with sculpted curved bevel
        rim_profile = [
            (rim_inner_r, z_pos - sign * (rim_thickness * 0.5)),
            (rim_outer_r - 0.008, z_pos - sign * (rim_thickness * 0.5)),
            (rim_outer_r, z_pos - sign * (rim_thickness * 0.15)),
            (rim_outer_r, z_pos + sign * (rim_thickness * 0.15)),
            (rim_outer_r - 0.008, z_pos + sign * (rim_thickness * 0.5)),
            (rim_inner_r, z_pos + sign * (rim_thickness * 0.5)),
        ]
        build_revolved_mesh(f"Rim_Hoop_{suffix}", rim_profile, segments=48, material=mat_rim, parent=root)

        # Decorative lacquer bead trim on rim edge
        gold_rim_lip = [
            (rim_outer_r + 0.0005, z_pos - 0.003),
            (rim_outer_r + 0.0035, z_pos - 0.0015),
            (rim_outer_r + 0.0035, z_pos + 0.0015),
            (rim_outer_r + 0.0005, z_pos + 0.003),
        ]
        build_revolved_mesh(f"Rim_Gold_Bead_{suffix}", gold_rim_lip, segments=40, material=mat_gold, parent=root)

    # ----------------------------------------------------
    # 3. Metal Fittings & Cord Holes (Choushi / Kanagu)
    # ----------------------------------------------------
    # Traditional Tsuzumi drumheads have 5 or 6 (typically 5 for small ko-tsuzumi) cord holes
    # evenly distributed in the wooden rim with brass eyelets/studs.
    num_holes = 5
    hole_radius = 0.126
    top_z = 0.138
    bot_z = -0.138

    top_hole_coords = []
    bot_hole_coords = []

    for i in range(num_holes):
        # Top holes
        angle_top = 2.0 * math.pi * i / num_holes
        xt = math.cos(angle_top) * hole_radius
        yt = math.sin(angle_top) * hole_radius
        top_pos = Vector((xt, yt, top_z))
        top_hole_coords.append(top_pos)

        # Brass grommet / eyelet
        build_cylinder(f"Eyelet_Top_{i}", radius=0.008, height=0.026, segments=12, z_offset=top_z, material=mat_gold, parent=root).location = (xt, yt, 0.0)

        # Bottom holes: staggered by half-segment for authentic zigzag lacing
        angle_bot = 2.0 * math.pi * (i + 0.5) / num_holes
        xb = math.cos(angle_bot) * hole_radius
        yb = math.sin(angle_bot) * hole_radius
        bot_pos = Vector((xb, yb, bot_z))
        bot_hole_coords.append(bot_pos)

        # Brass grommet / eyelet bottom
        build_cylinder(f"Eyelet_Bot_{i}", radius=0.008, height=0.026, segments=12, z_offset=bot_z, material=mat_gold, parent=root).location = (xb, yb, 0.0)

        # Decorative brass boss studs on rim face
        for side, z_lvl in [("Top", top_z + 0.012), ("Bot", bot_z - 0.012)]:
            ang = angle_top if side == "Top" else angle_bot
            sx = math.cos(ang) * (rim_outer_r - 0.006)
            sy = math.sin(ang) * (rim_outer_r - 0.006)
            build_cylinder(f"Stud_{side}_{i}", radius=0.0035, height=0.004, segments=8, z_offset=z_lvl, material=mat_gold, parent=root).location = (sx, sy, 0.0)

    # ----------------------------------------------------
    # 4. Vertical Zig-Zag Tension Cords (Tate-o / 縦緒)
    # ----------------------------------------------------
    # Thick vermilion-orange twisted hemp cords running tautly between top and bottom rims,
    # pulled inwards near the waist.
    waist_cinch_r = 0.056
    cord_thickness = 0.0038

    for i in range(num_holes):
        p_top1 = top_hole_coords[i]
        p_bot1 = bot_hole_coords[i]
        next_top_idx = (i + 1) % num_holes
        p_top2 = top_hole_coords[next_top_idx]

        # Downward path: top_i -> bot_i (curving in at the waist)
        mid_ang1 = math.atan2(p_top1.y + p_bot1.y, p_top1.x + p_bot1.x)
        mid_pt1 = Vector((math.cos(mid_ang1) * waist_cinch_r, math.sin(mid_ang1) * waist_cinch_r, 0.0))

        down_path = [
            p_top1 + Vector((0.0, 0.0, -0.008)),
            p_top1 * 0.75 + mid_pt1 * 0.25 + Vector((0.0, 0.0, 0.02)),
            mid_pt1,
            p_bot1 * 0.75 + mid_pt1 * 0.25 - Vector((0.0, 0.0, 0.02)),
            p_bot1 + Vector((0.0, 0.0, 0.008)),
        ]
        build_tube_along_points(f"Tate_O_Down_{i}", down_path, radius=cord_thickness, segments=8, material=mat_tate_o, parent=root)

        # Upward path: bot_i -> top_(i+1)
        mid_ang2 = math.atan2(p_bot1.y + p_top2.y, p_bot1.x + p_top2.x)
        mid_pt2 = Vector((math.cos(mid_ang2) * waist_cinch_r, math.sin(mid_ang2) * waist_cinch_r, 0.004))

        up_path = [
            p_bot1 + Vector((0.0, 0.0, 0.008)),
            p_bot1 * 0.75 + mid_pt2 * 0.25 - Vector((0.0, 0.0, 0.02)),
            mid_pt2,
            p_top2 * 0.75 + mid_pt2 * 0.25 + Vector((0.0, 0.0, 0.02)),
            p_top2 + Vector((0.0, 0.0, -0.008)),
        ]
        build_tube_along_points(f"Tate_O_Up_{i}", up_path, radius=cord_thickness, segments=8, material=mat_tate_o, parent=root)

        # Outer rim loop loops through the hole across the rim rim face
        loop_top_path = [
            p_top1 + Vector((0.0, 0.0, -0.008)),
            p_top1 + Vector((math.cos(math.atan2(p_top1.y, p_top1.x)) * 0.006, math.sin(math.atan2(p_top1.y, p_top1.x)) * 0.006, 0.014)),
            p_top1 + Vector((0.0, 0.0, 0.016)),
        ]
        build_tube_along_points(f"Rim_Loop_Top_{i}", loop_top_path, radius=cord_thickness * 0.9, segments=6, material=mat_tate_o, parent=root)

    # ----------------------------------------------------
    # 5. Waist Horizontal Tuning Cords (Momi-o / 揉緒 & Keshou-o)
    # ----------------------------------------------------
    # Dark contrasting cords tightly wound multiple times around the drum's waist,
    # binding all tension cords together to create the distinctive tsuzumi choke.
    wrap_radius = waist_cinch_r + 0.0045
    momi_rings = 4
    for ring in range(momi_rings):
        z_level = -0.014 + (ring * 0.009)
        ring_profile = [
            (wrap_radius - 0.003, z_level - 0.0035),
            (wrap_radius + 0.0035, z_level - 0.002),
            (wrap_radius + 0.0035, z_level + 0.002),
            (wrap_radius - 0.003, z_level + 0.0035),
        ]
        build_revolved_mesh(f"Momi_O_Band_{ring}", ring_profile, segments=36, material=mat_momi_o, parent=root)

    # Lateral knot and clasp on the tuning cord (Musubi)
    knot_pos = Vector((wrap_radius + 0.008, 0.0, 0.002))
    build_cylinder("Cord_Clasp", radius=0.008, height=0.026, segments=10, z_offset=0.002, material=mat_gold, parent=root).location = (knot_pos.x, knot_pos.y, 0.0)

    # Hanging ornamental adjustment cords and tassels (Tsuzumi Fusa / Kazari-himo)
    tassel_hang1 = [
        knot_pos + Vector((0.0, 0.004, 0.01)),
        knot_pos + Vector((0.012, 0.01, -0.04)),
        knot_pos + Vector((0.018, 0.015, -0.11)),
        knot_pos + Vector((0.024, 0.020, -0.19)),
    ]
    build_tube_along_points("Tassel_Cord_1", tassel_hang1, radius=0.003, segments=6, material=mat_purple_silk, parent=root)

    tassel_hang2 = [
        knot_pos + Vector((0.0, -0.004, 0.005)),
        knot_pos + Vector((0.014, -0.008, -0.05)),
        knot_pos + Vector((0.022, -0.012, -0.13)),
        knot_pos + Vector((0.028, -0.016, -0.21)),
    ]
    build_tube_along_points("Tassel_Cord_2", tassel_hang2, radius=0.003, segments=6, material=mat_purple_silk, parent=root)

    # Tassel tips / fringe cones
    tassel_tip1 = [
        (0.0, -0.19),
        (0.010, -0.20),
        (0.014, -0.235),
        (0.002, -0.24),
        (0.0, -0.24),
    ]
    cone1 = build_revolved_mesh("Tassel_Cone_1", tassel_tip1, segments=16, material=mat_purple_silk, parent=root)
    cone1.location = (knot_pos.x + 0.024, knot_pos.y + 0.020, 0.0)

    cone2 = build_revolved_mesh("Tassel_Cone_2", tassel_tip1, segments=16, material=mat_purple_silk, parent=root)
    cone2.location = (knot_pos.x + 0.028, knot_pos.y - 0.016, -0.02)

    # Small brass ferrule heads above tassels
    build_cylinder("Tassel_Cap_1", radius=0.0055, height=0.008, segments=10, z_offset=-0.188, material=mat_gold, parent=root).location = (knot_pos.x + 0.024, knot_pos.y + 0.020, 0.0)
    build_cylinder("Tassel_Cap_2", radius=0.0055, height=0.008, segments=10, z_offset=-0.208, material=mat_gold, parent=root).location = (knot_pos.x + 0.028, knot_pos.y - 0.016, 0.0)

    return root
