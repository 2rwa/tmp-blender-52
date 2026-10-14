import bpy
import math
from mathutils import Vector, Matrix, Euler

def create_material(name, diffuse_color, roughness=0.7, metallic=0.0, emission_color=None, emission_strength=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            # Base color
            if hasattr(bsdf.inputs["Base Color"], "default_value"):
                bsdf.inputs["Base Color"].default_value = diffuse_color
            if hasattr(bsdf.inputs["Roughness"], "default_value"):
                bsdf.inputs["Roughness"].default_value = roughness
            if hasattr(bsdf.inputs["Metallic"], "default_value"):
                bsdf.inputs["Metallic"].default_value = metallic
            # Emission
            if emission_strength > 0.0 and emission_color:
                if "Emission Color" in bsdf.inputs:
                    bsdf.inputs["Emission Color"].default_value = emission_color
                elif "Emission" in bsdf.inputs:
                    bsdf.inputs["Emission"].default_value = emission_color
                if "Emission Strength" in bsdf.inputs:
                    bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat

def assign_material(obj, mat):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

def create_box(name, size, location=(0,0,0), rotation=(0,0,0), material=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(scale=True, location=False, rotation=False)
    obj.location = location
    obj.rotation_euler = rotation
    if material:
        assign_material(obj, material)
    return obj

def create_cylinder(name, radius, depth, vertices=16, location=(0,0,0), rotation=(0,0,0), material=None):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    if material:
        assign_material(obj, material)
    return obj

def build_model():
    # Materials
    mat_dark_timber = create_material("DarkTimber", (0.18, 0.11, 0.06, 1.0), roughness=0.85)
    mat_light_plank = create_material("LightPlank", (0.55, 0.40, 0.25, 1.0), roughness=0.7)
    mat_red_wood    = create_material("RedWood", (0.55, 0.08, 0.08, 1.0), roughness=0.6)
    mat_white_cloth = create_material("WhiteCloth", (0.9, 0.88, 0.82, 1.0), roughness=0.9)
    mat_lantern_glow= create_material("LanternGlow", (0.95, 0.2, 0.15, 1.0), roughness=0.4,
                                      emission_color=(1.0, 0.35, 0.1, 1.0), emission_strength=4.0)
    mat_roof_tile   = create_material("RoofTile", (0.12, 0.13, 0.14, 1.0), roughness=0.65)
    mat_taiko_body  = create_material("TaikoBody", (0.4, 0.05, 0.03, 1.0), roughness=0.35)
    mat_taiko_skin  = create_material("TaikoSkin", (0.85, 0.78, 0.65, 1.0), roughness=0.8)
    mat_black_iron  = create_material("BlackIron", (0.05, 0.05, 0.05, 1.0), roughness=0.4, metallic=0.9)
    mat_stone_base  = create_material("StoneBase", (0.35, 0.34, 0.32, 1.0), roughness=0.95)

    created_objects = []

    # 1. Foundation Stones (4 corners)
    post_dist_bottom = 2.4
    post_dist_top = 1.8
    height_stage = 3.6
    post_thick = 0.18

    corners = [
        (-1, -1),
        ( 1, -1),
        ( 1,  1),
        (-1,  1)
    ]

    for i, (cx, cy) in enumerate(corners):
        px = cx * post_dist_bottom
        py = cy * post_dist_bottom
        st = create_box(f"BaseStone_{i}", (0.5, 0.5, 0.2), location=(px, py, 0.1), material=mat_stone_base)
        created_objects.append(st)

    # 2. Main Inward-Battered 4 Posts
    for i, (cx, cy) in enumerate(corners):
        bx, by, bz = cx * post_dist_bottom, cy * post_dist_bottom, 0.2
        tx, ty, tz = cx * post_dist_top, cy * post_dist_top, height_stage + 2.8
        
        dx, dy, dz = tx - bx, ty - by, tz - bz
        length = math.sqrt(dx*dx + dy*dy + dz*dz)
        mid_x, mid_y, mid_z = (bx + tx) / 2.0, (by + ty) / 2.0, (bz + tz) / 2.0
        
        post = create_box(f"MainPost_{i}", (post_thick, post_thick, length), location=(mid_x, mid_y, mid_z), material=mat_dark_timber)
        
        # Tilt inward
        pitch = -math.atan2(dx, dz) if cy == 0 else math.atan2(dy, dz)
        # Compute exact rotation matrix/euler pointing from bottom to top
        v_dir = Vector((dx, dy, dz)).normalized()
        rot_quat = Vector((0, 0, 1)).rotation_difference(v_dir)
        post.rotation_euler = rot_quat.to_euler()
        created_objects.append(post)

    # 3. Horizontal Ring Beams at multiple tiers
    tiers = [1.2, 2.4, 3.6, 5.0, 6.2]
    for tier_idx, tz in enumerate(tiers):
        factor = tz / (height_stage + 2.8)
        cur_dist = post_dist_bottom + (post_dist_top - post_dist_bottom) * factor
        beam_thick = 0.14 if tz < 4.0 else 0.12
        beam_mat = mat_red_wood if tier_idx == 2 or tier_idx == 4 else mat_dark_timber

        # 4 sides
        side_coords = [
            ((0, -cur_dist, tz), (cur_dist * 2.2, beam_thick, beam_thick)),
            ((0,  cur_dist, tz), (cur_dist * 2.2, beam_thick, beam_thick)),
            ((-cur_dist, 0, tz), (beam_thick, cur_dist * 2.2, beam_thick)),
            (( cur_dist, 0, tz), (beam_thick, cur_dist * 2.2, beam_thick))
        ]
        for s_idx, (loc, sc) in enumerate(side_coords):
            bm = create_box(f"RingBeam_{tier_idx}_{s_idx}", sc, location=loc, material=beam_mat)
            created_objects.append(bm)

    # 4. Diagonal Cross-Bracings (X-braces) on Lower Levels
    for lvl, (z0, z1) in enumerate([(0.3, 1.2), (1.3, 2.4), (2.5, 3.6)]):
        f0 = z0 / (height_stage + 2.8)
        f1 = z1 / (height_stage + 2.8)
        d0 = post_dist_bottom + (post_dist_top - post_dist_bottom) * f0
        d1 = post_dist_bottom + (post_dist_top - post_dist_bottom) * f1

        for side in range(4):
            # Skip front lower bay for ladder access
            if lvl == 0 and side == 0:
                continue
            if lvl == 1 and side == 0:
                continue

            # End points for cross 1 and 2
            # Side 0: y=-d, x from -d to d
            # Side 1: y=+d, x from -d to d
            # Side 2: x=-d, y from -d to d
            # Side 3: x=+d, y from -d to d
            corners_2d = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
            c_a = corners_2d[side]
            c_b = corners_2d[(side + 1) % 4]

            pA0 = Vector((c_a[0]*d0, c_a[1]*d0, z0))
            pB0 = Vector((c_b[0]*d0, c_b[1]*d0, z0))
            pA1 = Vector((c_a[0]*d1, c_a[1]*d1, z1))
            pB1 = Vector((c_b[0]*d1, c_b[1]*d1, z1))

            for brace_idx, (p_start, p_end) in enumerate([(pA0, pB1), (pB0, pA1)]):
                vec = p_end - p_start
                blen = vec.length
                mid = (p_start + p_end) / 2.0
                rot_quat = Vector((0, 0, 1)).rotation_difference(vec.normalized())
                
                br = create_box(f"Brace_{lvl}_{side}_{brace_idx}", (0.07, 0.09, blen), location=mid, material=mat_dark_timber)
                br.rotation_euler = rot_quat.to_euler()
                created_objects.append(br)

    # 5. Middle Sub-Platform / Intermediate Joists
    # Floor Joists at Stage Level (z = 3.6)
    stage_half = 2.4
    joist_count = 9
    for j in range(joist_count):
        y_pos = -stage_half + (2.0 * stage_half / (joist_count - 1)) * j
        jst = create_box(f"StageJoist_{j}", (stage_half * 2.2, 0.12, 0.16), location=(0, y_pos, 3.65), material=mat_dark_timber)
        created_objects.append(jst)

    # Floor Decking Planks (Stage)
    plank_count = 22
    for p in range(plank_count):
        x_pos = -stage_half + (2.0 * stage_half / (plank_count - 1)) * p
        plk = create_box(f"StagePlank_{p}", (0.2, stage_half * 2.15, 0.04), location=(x_pos, 0, 3.75), material=mat_light_plank)
        created_objects.append(plk)

    # 6. Upper Stage Guardrails (Traditional Balustrade)
    rail_h = 0.85
    rail_z = 3.8 + rail_h
    # Handrails (4 sides)
    rail_coords = [
        ((0, -stage_half, rail_z), (stage_half * 2.1, 0.08, 0.1)),
        ((0,  stage_half, rail_z), (stage_half * 2.1, 0.08, 0.1)),
        ((-stage_half, 0, rail_z), (0.08, stage_half * 2.1, 0.1)),
        (( stage_half, 0, rail_z), (0.08, stage_half * 2.1, 0.1))
    ]
    for r_idx, (loc, sc) in enumerate(rail_coords):
        hr = create_box(f"HandRail_{r_idx}", sc, location=loc, material=mat_red_wood)
        created_objects.append(hr)

    # Mid rails & Balusters
    for side_idx, (cx, cy) in enumerate([(0, -1), (0, 1), (-1, 0), (1, 0)]):
        for bal in range(7):
            t = (bal - 3) / 3.0 * (stage_half * 0.88)
            # Leave entrance gap on front rail
            if side_idx == 0 and abs(t) < 0.5:
                continue
            if cx == 0:
                bx, by = t, cy * stage_half
            else:
                bx, by = cx * stage_half, t
            b_post = create_box(f"Baluster_{side_idx}_{bal}", (0.05, 0.05, rail_h), location=(bx, by, 3.8 + rail_h/2.0), material=mat_dark_timber)
            created_objects.append(b_post)

    # 7. Accessible Ladder to Upper Stage
    lad_bottom_y = -3.2
    lad_top_y = -post_dist_bottom * (height_stage / (height_stage + 2.8)) + 0.1
    lad_top_z = 3.75
    lad_bot_z = 0.0
    lad_dy = lad_top_y - lad_bottom_y
    lad_dz = lad_top_z - lad_bot_z
    lad_len = math.sqrt(lad_dy*lad_dy + lad_dz*lad_dz)
    lad_angle = math.atan2(lad_dy, lad_dz)

    for side_x in [-0.35, 0.35]:
        stringer = create_box(f"LadderStringer_{side_x}", (0.06, 0.14, lad_len),
                              location=(side_x, (lad_bottom_y + lad_top_y)/2.0, lad_top_z/2.0),
                              rotation=(lad_angle, 0, 0), material=mat_dark_timber)
        created_objects.append(stringer)

    # Rungs
    rung_count = 11
    for ri in range(1, rung_count):
        frac = ri / rung_count
        rz = lad_bot_z + frac * lad_dz
        ry = lad_bottom_y + frac * lad_dy
        rung = create_box(f"LadderRung_{ri}", (0.64, 0.05, 0.04), location=(0, ry, rz), rotation=(lad_angle, 0, 0), material=mat_light_plank)
        created_objects.append(rung)

    # 8. Decorative Festival Skirting / Cloth Drapes (Kou-haku Maku)
    curtain_z = 3.1
    curtain_len = post_dist_bottom * 1.85
    curtain_configs = [
        ((0, -curtain_len/2.0 - 0.15, curtain_z), (curtain_len, 0.02, 1.0)),
        ((0,  curtain_len/2.0 + 0.15, curtain_z), (curtain_len, 0.02, 1.0)),
        ((-curtain_len/2.0 - 0.15, 0, curtain_z), (0.02, curtain_len, 1.0)),
        (( curtain_len/2.0 + 0.15, 0, curtain_z), (0.02, curtain_len, 1.0)),
    ]
    for c_i, (cloc, cdim) in enumerate(curtain_configs):
        # Skip ladder entry side partially or make split
        if c_i == 0:
            continue
        curt = create_box(f"Curtain_{c_i}", cdim, location=cloc, material=mat_white_cloth)
        created_objects.append(curt)

    # 9. Center Ceremonial Taiko Drum & Stand (On Stage)
    # Stand legs
    drum_center_z = 4.7
    stand_cross = [
        ((0.35, 0, 4.05), (0.06, 0.5, 0.65), (0, 0.35, 0)),
        ((-0.35, 0, 4.05), (0.06, 0.5, 0.65), (0, -0.35, 0)),
        ((0, 0.2, 4.05), (0.65, 0.06, 0.65), (-0.35, 0, 0)),
        ((0, -0.2, 4.05), (0.65, 0.06, 0.65), (0.35, 0, 0))
    ]
    for st_i, (sloc, sdim, srot) in enumerate(stand_cross):
        st_obj = create_box(f"TaikoStand_{st_i}", sdim, location=sloc, rotation=srot, material=mat_dark_timber)
        created_objects.append(st_obj)

    # Drum Body (Barrel cylinder rotated sideways)
    taiko_barrel = create_cylinder("TaikoDrumBody", radius=0.48, depth=0.85, vertices=24,
                                   location=(0, 0, drum_center_z), rotation=(0, math.pi/2, 0), material=mat_taiko_body)
    created_objects.append(taiko_barrel)

    # Drum Skins on both sides
    for side_sign, s_name in [(-1, "Left"), (1, "Right")]:
        skin = create_cylinder(f"TaikoSkin_{s_name}", radius=0.43, depth=0.03, vertices=24,
                               location=(side_sign * 0.43, 0, drum_center_z), rotation=(0, math.pi/2, 0), material=mat_taiko_skin)
        created_objects.append(skin)
        # Rim studs / metal hoop
        hoop = create_cylinder(f"TaikoHoop_{s_name}", radius=0.49, depth=0.04, vertices=24,
                               location=(side_sign * 0.41, 0, drum_center_z), rotation=(0, math.pi/2, 0), material=mat_black_iron)
        created_objects.append(hoop)

    # Drumsticks (Bachi)
    bachi1 = create_cylinder("Bachi_1", radius=0.018, depth=0.42, vertices=10,
                             location=(0.15, 0.45, 4.35), rotation=(0.4, 0.3, 0.6), material=mat_light_plank)
    bachi2 = create_cylinder("Bachi_2", radius=0.018, depth=0.42, vertices=10,
                             location=(-0.15, 0.45, 4.35), rotation=(0.4, -0.3, -0.6), material=mat_light_plank)
    created_objects.extend([bachi1, bachi2])

    # 10. Multi-tiered Wooden / Tiled Overhanging Roof
    roof_base_z = 6.4
    eaves_spread = 2.6
    ridge_h = 1.0

    # Roof Primary Rafters / Ceiling Truss
    rafter_count = 6
    for rx in range(rafter_count):
        fx = -eaves_spread*0.8 + (1.6 * eaves_spread / (rafter_count - 1)) * rx
        r_beam = create_box(f"RoofTruss_{rx}", (0.1, eaves_spread * 1.8, 0.1), location=(fx, 0, roof_base_z - 0.1), material=mat_dark_timber)
        created_objects.append(r_beam)

    # Roof Slanted Panels (Irimoya / Kirizuma hip-gable style)
    roof_pitch = 0.42
    r_length = eaves_spread * 1.3
    r_width = eaves_spread * 2.2
    
    # North slope
    roof_n = create_box("RoofSlope_North", (r_width, r_length, 0.08),
                        location=(0, -0.9, roof_base_z + 0.45), rotation=(roof_pitch, 0, 0), material=mat_roof_tile)
    # South slope
    roof_s = create_box("RoofSlope_South", (r_width, r_length, 0.08),
                        location=(0,  0.9, roof_base_z + 0.45), rotation=(-roof_pitch, 0, 0), material=mat_roof_tile)
    created_objects.extend([roof_n, roof_s])

    # Ornamental Gable Bargeboards & Ridge Beam (Mune)
    ridge_beam = create_box("RoofRidgeBeam", (r_width * 1.05, 0.22, 0.25),
                            location=(0, 0, roof_base_z + ridge_h + 0.05), material=mat_dark_timber)
    ridge_tile = create_cylinder("RoofRidgeRoll", radius=0.12, depth=r_width * 1.06, vertices=16,
                                 location=(0, 0, roof_base_z + ridge_h + 0.16), rotation=(0, math.pi/2, 0), material=mat_roof_tile)
    created_objects.extend([ridge_beam, ridge_tile])

    # Roof Eaves Fascia trim boards
    fascia_n = create_box("Fascia_N", (r_width * 1.02, 0.06, 0.14), location=(0, -eaves_spread * 1.05, roof_base_z + 0.08), material=mat_red_wood)
    fascia_s = create_box("Fascia_S", (r_width * 1.02, 0.06, 0.14), location=(0,  eaves_spread * 1.05, roof_base_z + 0.08), material=mat_red_wood)
    created_objects.extend([fascia_n, fascia_s])

    # 11. Traditional Festival Lanterns (Chochin)
    lantern_positions = []
    # Perimeter of the upper deck eaves
    num_per_side = 4
    deck_span = eaves_spread * 0.92
    for s_step in range(num_per_side):
        frac = (s_step - (num_per_side-1)/2.0) / ((num_per_side-1)/2.0)
        offset = frac * (deck_span * 0.85)
        lantern_positions.append((offset, -deck_span, roof_base_z - 0.2))
        lantern_positions.append((offset,  deck_span, roof_base_z - 0.2))
        lantern_positions.append((-deck_span, offset, roof_base_z - 0.2))
        lantern_positions.append(( deck_span, offset, roof_base_z - 0.2))

    for l_idx, (lx, ly, lz) in enumerate(lantern_positions):
        # Suspension String / Rod
        rod = create_cylinder(f"LanternWire_{l_idx}", radius=0.007, depth=0.35, vertices=6,
                              location=(lx, ly, lz - 0.17), material=mat_black_iron)
        
        # Lantern Main Bulbous Ribbed Body
        l_body = create_cylinder(f"ChochinBody_{l_idx}", radius=0.17, depth=0.42, vertices=16,
                                 location=(lx, ly, lz - 0.45), material=mat_lantern_glow)
        
        # Black Cap and Base Rings
        l_top_cap = create_cylinder(f"ChochinTop_{l_idx}", radius=0.12, depth=0.04, vertices=16,
                                    location=(lx, ly, lz - 0.22), material=mat_black_iron)
        l_bot_cap = create_cylinder(f"ChochinBot_{l_idx}", radius=0.12, depth=0.04, vertices=16,
                                    location=(lx, ly, lz - 0.68), material=mat_black_iron)
        
        created_objects.extend([rod, l_body, l_top_cap, l_bot_cap])

    # Ensure all newly created objects are properly linked and selected
    for o in created_objects:
        if o.name not in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.link(o)

    return created_objects
