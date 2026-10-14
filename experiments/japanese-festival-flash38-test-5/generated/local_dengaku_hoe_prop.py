import bpy
import math
import mathutils

def create_material(name, diffuse_color, roughness=0.5, metallic=0.0):
    """Helper to create a standard Principled BSDF material in Blender 5.2."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        # Diffuse / Base Color
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = diffuse_color
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
    return mat

def build_model():
    """
    Constructs a detailed traditional Japanese Dengaku ceremonial hoe prop (dengaku-bitchu-guwa / binzasara/matsuri hoe).
    Consists of:
      1. Long polished wooden shaft (tsuka / e)
      2. Traditional wooden joint socket / angled tenon mounting block
      3. Broad flat ceremonial hoe blade (kuwa-ha) with carved profile and bevels
      4. Hand-forged metal reinforcement bands, rivets, and mounting sleeve
      5. Festive ceremonial ornaments: braided shimenawa-style hemp cord, hanging tassels (fusa),
         and ceremonial red/gold lacquered accent bands.
    """
    # -------------------------------------------------------------
    # Materials
    # -------------------------------------------------------------
    mat_wood_shaft = create_material("Mat_CypressWood_Shaft", (0.76, 0.58, 0.38, 1.0), roughness=0.45)
    mat_wood_dark = create_material("Mat_AgedWood_Mount", (0.35, 0.22, 0.12, 1.0), roughness=0.6)
    mat_ceremonial_blade = create_material("Mat_LacqueredWood_Blade", (0.55, 0.36, 0.22, 1.0), roughness=0.35)
    mat_iron = create_material("Mat_ForgedIron_Hardware", (0.12, 0.12, 0.13, 1.0), roughness=0.4, metallic=0.85)
    mat_brass = create_material("Mat_CeremonialBrass", (0.85, 0.65, 0.20, 1.0), roughness=0.3, metallic=0.9)
    mat_cord_red = create_material("Mat_FestiveCord_Vermilion", (0.82, 0.08, 0.05, 1.0), roughness=0.7)
    mat_cord_white = create_material("Mat_HempCord_Bleached", (0.92, 0.90, 0.82, 1.0), roughness=0.8)
    mat_gold_accent = create_material("Mat_GoldLeaf_Foil", (0.95, 0.75, 0.20, 1.0), roughness=0.25, metallic=0.95)

    created_objects = []

    # Helper function to create mesh from pydata
    def add_mesh_obj(name, verts, faces, material=None, location=(0, 0, 0), rotation=(0, 0, 0)):
        mesh = bpy.data.meshes.new(name + "_mesh")
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        obj.location = location
        obj.rotation_euler = rotation
        bpy.context.collection.objects.link(obj)
        if material:
            obj.data.materials.append(material)
        created_objects.append(obj)
        return obj

    # -------------------------------------------------------------
    # 1. Long Wooden Shaft (Tsuka)
    # Traditional Japanese long octagonal/slightly rounded hardwood staff
    # -------------------------------------------------------------
    shaft_len = 1.60
    shaft_r = 0.016
    segments = 10
    shaft_verts = []
    shaft_faces = []
    
    # 8-sided faceted profile slightly tapered toward the grip/butt
    for z_idx, z in enumerate([0.0, 0.4, 0.8, 1.2, shaft_len]):
        taper = 1.0 + 0.08 * (z / shaft_len)
        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            x = math.cos(angle) * shaft_r * taper
            y = math.sin(angle) * shaft_r * taper
            shaft_verts.append((x, y, z))

    for ring in range(4):
        offset1 = ring * segments
        offset2 = (ring + 1) * segments
        for i in range(segments):
            next_i = (i + 1) % segments
            shaft_faces.append([offset1 + i, offset1 + next_i, offset2 + next_i, offset2 + i])

    # End caps
    shaft_faces.append([i for i in range(segments - 1, -1, -1)])
    shaft_faces.append([4 * segments + i for i in range(segments)])

    obj_shaft = add_mesh_obj("Hoe_Wooden_Shaft", shaft_verts, shaft_faces, mat_wood_shaft)

    # Copper/Iron butt-cap (Ishizuki) at the bottom
    butt_verts = []
    butt_faces = []
    butt_h = 0.04
    butt_r = shaft_r * 1.05
    for i in range(segments):
        a = 2.0 * math.pi * i / segments
        butt_verts.append((math.cos(a) * butt_r, math.sin(a) * butt_r, -0.005))
    for i in range(segments):
        a = 2.0 * math.pi * i / segments
        butt_verts.append((math.cos(a) * butt_r, math.sin(a) * butt_r, butt_h))
    for i in range(segments):
        ni = (i + 1) % segments
        butt_faces.append([i, ni, segments + ni, segments + i])
    butt_faces.append([i for i in range(segments - 1, -1, -1)])
    butt_faces.append([segments + i for i in range(segments)])
    add_mesh_obj("Shaft_ButtCap", butt_verts, butt_faces, mat_iron)

    # -------------------------------------------------------------
    # 2. Mounting Head Block & Joinery Joint (Hizoke / E-gashira)
    # Japanese agricultural hoes feature a distinctive hardwood throat block
    # angled at ~60-70 degrees to hold the blade.
    # -------------------------------------------------------------
    neck_z = shaft_len - 0.04
    mount_w = 0.046
    mount_d = 0.052
    mount_h = 0.11

    # Block at the top of the shaft
    mb_verts = [
        (-mount_w*0.5, -mount_d*0.5, 0),
        ( mount_w*0.5, -mount_d*0.5, 0),
        ( mount_w*0.5,  mount_d*0.5, 0),
        (-mount_w*0.5,  mount_d*0.5, 0),
        (-mount_w*0.48, -mount_d*0.45, mount_h),
        ( mount_w*0.48, -mount_d*0.45, mount_h),
        ( mount_w*0.48,  mount_d*0.65, mount_h),
        (-mount_w*0.48,  mount_d*0.65, mount_h),
    ]
    mb_faces = [
        [0, 1, 2, 3],
        [4, 7, 6, 5],
        [0, 4, 5, 1],
        [1, 5, 6, 2],
        [2, 6, 7, 3],
        [3, 7, 4, 0]
    ]
    add_mesh_obj("Hoe_MountingJointBlock", mb_verts, mb_faces, mat_wood_dark, location=(0, 0, neck_z))

    # Iron ferrule sleeve collar wrapping around the joint
    collar_verts = []
    collar_faces = []
    c_r = 0.024
    c_h = 0.05
    for ring_z in [0.0, c_h]:
        for i in range(segments):
            a = 2.0 * math.pi * i / segments
            collar_verts.append((math.cos(a) * c_r, math.sin(a) * c_r, ring_z))
    for i in range(segments):
        ni = (i + 1) % segments
        collar_faces.append([i, ni, segments + ni, segments + i])
    collar_faces.append([i for i in range(segments - 1, -1, -1)])
    collar_faces.append([segments + i for i in range(segments)])
    add_mesh_obj("Shaft_FerruleCollar", collar_verts, collar_faces, mat_iron, location=(0, 0, neck_z - 0.03))

    # -------------------------------------------------------------
    # 3. Broad Flat Ceremonial Hoe Head (Kuwa-Ha)
    # Traditional Dengaku dance prop blade: broad, carved shoulder,
    # gently flared bottom edge, wedge bevel, festive carved crest.
    # -------------------------------------------------------------
    # Blade pivot angle relative to shaft (bent downward around 68 degrees)
    blade_angle = math.radians(68.0)
    # The blade extends in negative Y and downward in local rotation
    blade_top_w = 0.13
    blade_bot_w = 0.22
    blade_len = 0.34
    blade_t = 0.018

    # Profile coordinates along blade length:
    # y goes forward/down along blade, z is thickness, x is width
    b_sections = [
        # (local_y, half_width, thickness)
        (0.00,  0.045, blade_t * 1.3),  # Tang / shoulder insertion
        (0.05,  0.070, blade_t * 1.1),  # Neck flare
        (0.12,  0.085, blade_t * 1.0),  # Upper body
        (0.24,  0.100, blade_t * 0.85), # Mid blade
        (0.32,  0.115, blade_t * 0.55), # Lower edge approach
        (0.35,  0.118, 0.002)           # Cutting edge bevel
    ]

    blade_verts = []
    blade_faces = []
    n_sec = len(b_sections)

    for y_val, hw, thick in b_sections:
        # 4 vertices per cross section: (-x, thick/2), (+x, thick/2), (+x, -thick/2), (-x, -thick/2)
        blade_verts.append((-hw, y_val,  thick * 0.5))
        blade_verts.append(( hw, y_val,  thick * 0.5))
        blade_verts.append(( hw, y_val, -thick * 0.5))
        blade_verts.append((-hw, y_val, -thick * 0.5))

    for s in range(n_sec - 1):
        o1 = s * 4
        o2 = (s + 1) * 4
        # Top face
        blade_faces.append([o1 + 0, o2 + 0, o2 + 1, o1 + 1])
        # Right face
        blade_faces.append([o1 + 1, o2 + 1, o2 + 2, o1 + 2])
        # Bottom face
        blade_faces.append([o1 + 2, o2 + 2, o2 + 3, o1 + 3])
        # Left face
        blade_faces.append([o1 + 3, o2 + 3, o2 + 0, o1 + 0])

    # Cap at base and tip
    blade_faces.append([3, 2, 1, 0])
    last_o = (n_sec - 1) * 4
    blade_faces.append([last_o + 0, last_o + 1, last_o + 2, last_o + 3])

    blade_origin = (0, 0.02, neck_z + 0.06)
    blade_rot = (blade_angle, 0, 0)
    obj_blade = add_mesh_obj("Hoe_CeremonialBlade", blade_verts, blade_faces, mat_ceremonial_blade,
                             location=blade_origin, rotation=blade_rot)

    # -------------------------------------------------------------
    # 4. Iron Tang Clamps, Wedge (Mekugi) & Rivets
    # -------------------------------------------------------------
    # Two forged iron strapping bands clamping the blade root onto the wooden elbow
    for band_y in [0.03, 0.08]:
        band_w = 0.09
        band_d = 0.012
        band_h = 0.028
        b_verts = [
            (-band_w*0.5, band_y - band_d*0.5, -band_h*0.5),
            ( band_w*0.5, band_y - band_d*0.5, -band_h*0.5),
            ( band_w*0.5, band_y + band_d*0.5, -band_h*0.5),
            (-band_w*0.5, band_y + band_d*0.5, -band_h*0.5),
            (-band_w*0.5, band_y - band_d*0.5,  band_h*0.5),
            ( band_w*0.5, band_y - band_d*0.5,  band_h*0.5),
            ( band_w*0.5, band_y + band_d*0.5,  band_h*0.5),
            (-band_w*0.5, band_y + band_d*0.5,  band_h*0.5),
        ]
        b_faces = [
            [0, 1, 2, 3], [4, 7, 6, 5],
            [0, 4, 5, 1], [1, 5, 6, 2],
            [2, 6, 7, 3], [3, 7, 4, 0]
        ]
        add_mesh_obj(f"Blade_ClampBand_{int(band_y*100)}", b_verts, b_faces, mat_iron,
                     location=blade_origin, rotation=blade_rot)

    # Brass decorative rivets on the blade (Kugi / Hoshi ornaments)
    for rx in [-0.04, 0.0, 0.04]:
        r_verts = []
        r_faces = []
        rr = 0.007
        rh = 0.008
        for i in range(8):
            a = 2.0 * math.pi * i / 8
            r_verts.append((rx + math.cos(a)*rr, 0.16, math.sin(a)*rr))
        for i in range(8):
            a = 2.0 * math.pi * i / 8
            r_verts.append((rx + math.cos(a)*rr*0.7, 0.16 + rh, math.sin(a)*rr*0.7))
        for i in range(8):
            ni = (i + 1) % 8
            r_faces.append([i, ni, 8 + ni, 8 + i])
        r_faces.append([i for i in range(7, -1, -1)])
        r_faces.append([8 + i for i in range(8)])
        add_mesh_obj(f"Ceremonial_Rivet_{rx}", r_verts, r_faces, mat_brass,
                     location=blade_origin, rotation=blade_rot)

    # -------------------------------------------------------------
    # 5. Ceremonial Lacquered Crest Inlay (Mitsu-Tomoe / Sun motif)
    # Center medallion on the ceremonial blade face
    # -------------------------------------------------------------
    emblem_verts = []
    emblem_faces = []
    emblem_r = 0.026
    em_thick = 0.004
    for i in range(12):
        a = 2.0 * math.pi * i / 12
        emblem_verts.append((math.cos(a) * emblem_r, 0.22, math.sin(a) * emblem_r))
    for i in range(12):
        a = 2.0 * math.pi * i / 12
        emblem_verts.append((math.cos(a) * emblem_r, 0.22 + em_thick, math.sin(a) * emblem_r))
    for i in range(12):
        ni = (i + 1) % 12
        emblem_faces.append([i, ni, 12 + ni, 12 + i])
    emblem_faces.append([i for i in range(11, -1, -1)])
    emblem_faces.append([12 + i for i in range(12)])
    add_mesh_obj("Blade_Ceremonial_SunCrest", emblem_verts, emblem_faces, mat_gold_accent,
                 location=blade_origin, rotation=blade_rot)

    # -------------------------------------------------------------
    # 6. Ceremonial Braided Shimenawa / Festive Cord Wrap
    # Wound around the junction of shaft and hoe blade neck
    # -------------------------------------------------------------
    cord_turns = 6
    cord_pts_per_turn = 12
    total_pts = cord_turns * cord_pts_per_turn
    cord_radius = 0.027
    cord_thick = 0.0055

    cord_verts = []
    cord_faces = []
    
    # Generate helical spiral cord tube
    curve_points = []
    for step in range(total_pts):
        t = step / total_pts
        angle = t * cord_turns * 2.0 * math.pi
        z = neck_z - 0.08 + t * 0.075
        x = math.cos(angle) * (cord_radius + 0.003 * math.sin(angle * 3))
        y = math.sin(angle) * (cord_radius + 0.003 * math.sin(angle * 3))
        curve_points.append(mathutils.Vector((x, y, z)))

    for i in range(len(curve_points) - 1):
        p0 = curve_points[i]
        p1 = curve_points[i + 1]
        tangent = (p1 - p0).normalized()
        up = mathutils.Vector((0, 0, 1))
        norm = tangent.cross(up).normalized()
        binorm = tangent.cross(norm).normalized()

        base_idx = len(cord_verts)
        # 4-sided cross section for low poly crispness and efficiency
        for side in range(4):
            ca = 2.0 * math.pi * side / 4.0
            offset = (norm * math.cos(ca) + binorm * math.sin(ca)) * cord_thick
            v = p0 + offset
            cord_verts.append((v.x, v.y, v.z))

    segments_tube = len(curve_points) - 1
    for seg in range(segments_tube - 1):
        o1 = seg * 4
        o2 = (seg + 1) * 4
        for s in range(4):
            ns = (s + 1) % 4
            cord_faces.append([o1 + s, o1 + ns, o2 + ns, o2 + s])

    add_mesh_obj("Shaft_FestiveCordWrap", cord_verts, cord_faces, mat_cord_red)

    # -------------------------------------------------------------
    # 7. Hanging Ceremonial Dengaku Tassels (Fusa)
    # Suspended from the throat joint on left and right sides
    # -------------------------------------------------------------
    for side_sign in [-1.0, 1.0]:
        tassel_anchor_x = side_sign * 0.038
        tassel_anchor_y = 0.015
        tassel_anchor_z = neck_z - 0.02

        # Upper suspension string
        tstr_verts = [
            (tassel_anchor_x, tassel_anchor_y, tassel_anchor_z),
            (tassel_anchor_x * 1.1, tassel_anchor_y, tassel_anchor_z - 0.07),
            (tassel_anchor_x * 1.1 + 0.004, tassel_anchor_y, tassel_anchor_z - 0.07),
            (tassel_anchor_x + 0.004, tassel_anchor_y, tassel_anchor_z)
        ]
        tstr_faces = [[0, 1, 2, 3]]
        add_mesh_obj(f"Tassel_String_{int(side_sign)}", tstr_verts, tstr_faces, mat_cord_white)

        # Ornamental Knot Bead (Agemaki bead)
        bead_r = 0.010
        bead_h = 0.016
        b_verts = []
        b_faces = []
        for i in range(8):
            a = 2.0 * math.pi * i / 8
            b_verts.append((math.cos(a)*bead_r, math.sin(a)*bead_r, 0.0))
        for i in range(8):
            a = 2.0 * math.pi * i / 8
            b_verts.append((math.cos(a)*bead_r, math.sin(a)*bead_r, -bead_h))
        for i in range(8):
            ni = (i + 1) % 8
            b_faces.append([i, ni, 8 + ni, 8 + i])
        b_faces.append([i for i in range(7, -1, -1)])
        b_faces.append([8 + i for i in range(8)])
        add_mesh_obj(f"Tassel_Knot_{int(side_sign)}", b_verts, b_faces, mat_brass,
                     location=(tassel_anchor_x * 1.1, tassel_anchor_y, tassel_anchor_z - 0.07))

        # Flared fringe skirt tassel (Fusa)
        fusa_h = 0.14
        top_fr = 0.009
        bot_fr = 0.024
        f_verts = []
        f_faces = []
        f_segs = 8
        for i in range(f_segs):
            a = 2.0 * math.pi * i / f_segs
            f_verts.append((math.cos(a) * top_fr, math.sin(a) * top_fr, 0.0))
        for i in range(f_segs):
            a = 2.0 * math.pi * i / f_segs
            f_verts.append((math.cos(a) * bot_fr, math.sin(a) * bot_fr, -fusa_h))
        for i in range(f_segs):
            ni = (i + 1) % f_segs
            f_faces.append([i, ni, f_segs + ni, f_segs + i])
        f_faces.append([i for i in range(f_segs - 1, -1, -1)])
        f_faces.append([f_segs + i for i in range(f_segs)])
        add_mesh_obj(f"Ceremonial_Fusa_{int(side_sign)}", f_verts, f_faces, mat_cord_red,
                     location=(tassel_anchor_x * 1.1, tassel_anchor_y, tassel_anchor_z - 0.086))

    # -------------------------------------------------------------
    # 8. Sacred Shide (Paper streamers) folded zigzag accents
    # Characteristic Shinto/Dengaku celebratory streamers tied to prop
    # -------------------------------------------------------------
    shide_verts = [
        (-0.015, -0.025, neck_z - 0.03),
        ( 0.005, -0.025, neck_z - 0.03),
        (-0.022, -0.026, neck_z - 0.065),
        (-0.002, -0.026, neck_z - 0.065),
        (-0.008, -0.027, neck_z - 0.100),
        ( 0.012, -0.027, neck_z - 0.100),
        (-0.016, -0.028, neck_z - 0.135),
        ( 0.004, -0.028, neck_z - 0.135),
    ]
    shide_faces = [
        [0, 1, 3, 2],
        [2, 3, 5, 4],
        [4, 5, 7, 6],
    ]
    add_mesh_obj("Ceremonial_ShideStreamer", shide_verts, shide_faces, mat_cord_white)

    # -------------------------------------------------------------
    # 9. Grip Section / Hand Positioning Markings (Urushi Lacquer rings)
    # Distinctive vermilion lacquer segments on the handle for performance grip
    # -------------------------------------------------------------
    grip_heights = [0.55, 0.60, 0.65, 0.90, 0.95, 1.00]
    for idx, gh in enumerate(grip_heights):
        ring_v = []
        ring_f = []
        rr = shaft_r * 1.03
        rh = 0.016
        for i in range(segments):
            a = 2.0 * math.pi * i / segments
            ring_v.append((math.cos(a) * rr, math.sin(a) * rr, 0.0))
        for i in range(segments):
            a = 2.0 * math.pi * i / segments
            ring_v.append((math.cos(a) * rr, math.sin(a) * rr, rh))
        for i in range(segments):
            ni = (i + 1) % segments
            ring_f.append([i, ni, segments + ni, segments + i])
        ring_f.append([i for i in range(segments - 1, -1, -1)])
        ring_f.append([segments + i for i in range(segments)])
        add_mesh_obj(f"Shaft_GripRing_{idx}", ring_v, ring_f, mat_cord_red, location=(0, 0, gh))

    # Parent all parts to the main shaft for convenient scene manipulation
    for obj in created_objects:
        if obj != obj_shaft:
            obj.parent = obj_shaft

    return obj_shaft
