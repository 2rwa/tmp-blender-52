import bpy
import math
from mathutils import Vector, Matrix

def create_material(name, base_color, roughness=0.3, metallic=0.0, specular=0.5):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = base_color
            bsdf.inputs['Roughness'].default_value = roughness
            bsdf.inputs['Metallic'].default_value = metallic
            if 'Specular IOR Level' in bsdf.inputs:
                bsdf.inputs['Specular IOR Level'].default_value = specular
            elif 'Specular' in bsdf.inputs:
                bsdf.inputs['Specular'].default_value = specular
    return mat

def create_cylinder_mesh(name, radius_top, radius_bottom, depth, radial_segments=32, cap_ends=True):
    mesh = bpy.data.meshes.new(name)
    verts = []
    faces = []
    
    half_d = depth / 2.0
    # Bottom ring: 0 to radial_segments-1
    # Top ring: radial_segments to 2*radial_segments-1
    for i in range(radial_segments):
        theta = 2.0 * math.pi * i / radial_segments
        x_b = radius_bottom * math.cos(theta)
        y_b = radius_bottom * math.sin(theta)
        verts.append(Vector((x_b, y_b, -half_d)))
        
    for i in range(radial_segments):
        theta = 2.0 * math.pi * i / radial_segments
        x_t = radius_top * math.cos(theta)
        y_t = radius_top * math.sin(theta)
        verts.append(Vector((x_t, y_t, half_d)))
        
    for i in range(radial_segments):
        i_next = (i + 1) % radial_segments
        v0 = i
        v1 = i_next
        v2 = i_next + radial_segments
        v3 = i + radial_segments
        faces.append([v0, v1, v2, v3])
        
    if cap_ends:
        # Bottom cap
        faces.append(list(reversed(range(radial_segments))))
        # Top cap
        faces.append(list(range(radial_segments, 2 * radial_segments)))
        
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return mesh

def build_model():
    # -------------------------------------------------------------
    # 1. Materials for Ryuteki (Traditional Gagaku Court Flute)
    # -------------------------------------------------------------
    # Lacquered outer bamboo/bark (Kaba-maki / Urushi dark reddish black/amber)
    mat_outer_lacquer = create_material("Ryuteki_BlackUrushi", (0.04, 0.02, 0.02, 1.0), roughness=0.18, specular=0.7)
    # Bright Vermilion red inner bore lacquer (Shu-urushi)
    mat_inner_bore = create_material("Ryuteki_RedUrushi", (0.75, 0.05, 0.02, 1.0), roughness=0.25, specular=0.5)
    # Silk/bark cord bindings (Cherry bark / silk thread wrapping)
    mat_binding = create_material("Ryuteki_ThreadBinding", (0.08, 0.045, 0.03, 1.0), roughness=0.6, specular=0.2)
    # Metal/Horn fittings at ends (Kashira-gane / silver or pewter ornament, bone/horn trim)
    mat_metal_fitting = create_material("Ryuteki_SilverOrnament", (0.75, 0.73, 0.70, 1.0), roughness=0.25, metallic=0.9)
    # Wooden interior plug (Omoi-koto cork/lead plug wrapped in paper/cloth)
    mat_plug = create_material("Ryuteki_LeadWaxPlug", (0.15, 0.12, 0.10, 1.0), roughness=0.5)
    # Decorative red silk tassel cord
    mat_tassel = create_material("Ryuteki_SilkCord", (0.8, 0.03, 0.04, 1.0), roughness=0.5)

    # -------------------------------------------------------------
    # Ryuteki Dimensions (Approx 40 cm total length)
    # Aligned horizontally along the X-axis for natural flute display
    # -------------------------------------------------------------
    total_len = 0.400 # 400 mm
    outer_r_mouth = 0.0125 # 25 mm diameter near blowhole
    outer_r_tail = 0.0105  # slightly tapered to 21 mm at foot
    inner_r = 0.0075       # 15 mm bore
    wall_thickness = 0.0035

    # Master Ryuteki Root Object
    ryuteki_root = bpy.data.objects.new("Ryuteki_Flute", None)
    bpy.context.scene.collection.objects.link(ryuteki_root)
    ryuteki_root.location = (0, 0, 0.03)

    # -------------------------------------------------------------
    # 2. Outer Flute Pipe Body (Constructed with longitudinal segments)
    # -------------------------------------------------------------
    # We build the flute horizontally along X from x = -0.09 (head) to x = 0.31 (foot)
    head_x = -0.090
    foot_x = 0.310
    length_x = foot_x - head_x
    
    pipe_subdiv_x = 80
    radial_seg = 36
    
    verts = []
    faces = []
    
    # Generate outer and inner tube surface
    # Ring indices: 
    # Outer rings: ring 0 to pipe_subdiv_x
    # Inner rings: ring pipe_subdiv_x + 1 to 2*(pipe_subdiv_x + 1) - 1
    for r_idx in range(pipe_subdiv_x + 1):
        u = r_idx / pipe_subdiv_x
        x = head_x + u * length_x
        curr_outer_r = outer_r_mouth - u * (outer_r_mouth - outer_r_tail)
        
        for s in range(radial_seg):
            theta = 2.0 * math.pi * s / radial_seg
            y = curr_outer_r * math.cos(theta)
            z = curr_outer_r * math.sin(theta)
            verts.append(Vector((x, y, z)))
            
    outer_v_count = len(verts)

    # Inner bore vertices
    for r_idx in range(pipe_subdiv_x + 1):
        u = r_idx / pipe_subdiv_x
        x = head_x + u * length_x
        for s in range(radial_seg):
            theta = 2.0 * math.pi * s / radial_seg
            y = inner_r * math.cos(theta)
            z = inner_r * math.sin(theta)
            verts.append(Vector((x, y, z)))

    # Outer tube quads
    for r_idx in range(pipe_subdiv_x):
        r_start = r_idx * radial_seg
        r_next = (r_idx + 1) * radial_seg
        for s in range(radial_seg):
            s_next = (s + 1) % radial_seg
            faces.append([r_start + s, r_next + s, r_next + s_next, r_start + s_next])
            
    # Inner tube quads (pointing inward)
    for r_idx in range(pipe_subdiv_x):
        r_start = outer_v_count + r_idx * radial_seg
        r_next = outer_v_count + (r_idx + 1) * radial_seg
        for s in range(radial_seg):
            s_next = (s + 1) % radial_seg
            faces.append([r_start + s, r_start + s_next, r_next + s_next, r_next + s])

    # End cap rims connecting outer to inner at head and foot
    # Head rim (x = head_x)
    for s in range(radial_seg):
        s_next = (s + 1) % radial_seg
        v_out_0 = s
        v_out_1 = s_next
        v_in_0 = outer_v_count + s
        v_in_1 = outer_v_count + s_next
        faces.append([v_out_0, v_in_0, v_in_1, v_out_1])

    # Foot rim (x = foot_x)
    foot_out_base = pipe_subdiv_x * radial_seg
    foot_in_base = outer_v_count + pipe_subdiv_x * radial_seg
    for s in range(radial_seg):
        s_next = (s + 1) % radial_seg
        v_out_0 = foot_out_base + s
        v_out_1 = foot_out_base + s_next
        v_in_0 = foot_in_base + s
        v_in_1 = foot_in_base + s_next
        faces.append([v_out_0, v_out_1, v_in_1, v_in_0])

    flute_mesh = bpy.data.meshes.new("Ryuteki_MainTube")
    flute_mesh.from_pydata(verts, [], faces)
    flute_mesh.update()
    
    flute_obj = bpy.data.objects.new("Ryuteki_MainTube", flute_mesh)
    flute_obj.data.materials.append(mat_outer_lacquer)
    flute_obj.data.materials.append(mat_inner_bore)
    bpy.context.scene.collection.objects.link(flute_obj)
    flute_obj.parent = ryuteki_root

    # Colorize inside bore polygons as red lacquer
    for p in flute_mesh.polygons:
        # If normal points inward or polygon center radius is close to inner_r
        c = p.center
        rad = math.sqrt(c.y * c.y + c.z * c.z)
        if rad <= inner_r + 0.0005:
            p.material_index = 1
        else:
            p.material_index = 0

    # -------------------------------------------------------------
    # 3. Tone Holes & Embouchure Cutters (Procedural Carving)
    # Traditional Ryuteki layout:
    # 1 Utaguchi (embouchure blow hole) + 7 Yubi-ana (finger holes)
    # Positions along X axis:
    # Utaguchi: ~ 0.000 m
    # Finger holes 1 to 7: from ~0.100 m to ~0.260 m
    # -------------------------------------------------------------
    hole_specs = [
        ("Utaguchi_Embouchure", 0.000, 0.0068, 0.0055), # Oval / large blow hole
        ("Yubiana_1", 0.105, 0.0042, 0.0042),
        ("Yubiana_2", 0.130, 0.0042, 0.0042),
        ("Yubiana_3", 0.155, 0.0040, 0.0040),
        ("Yubiana_4", 0.182, 0.0040, 0.0040),
        ("Yubiana_5", 0.208, 0.0040, 0.0040),
        ("Yubiana_6", 0.234, 0.0039, 0.0039),
        ("Yubiana_7", 0.258, 0.0038, 0.0038),
    ]

    cutter_objs = []
    rim_collars = []

    for name, pos_x, rad_y, rad_x in hole_specs:
        # Create an elliptical cylinder cutter
        cutter_mesh = create_cylinder_mesh(f"Cutter_{name}", 1.0, 1.0, 0.04, radial_segments=28, cap_ends=True)
        cutter_obj = bpy.data.objects.new(f"Cutter_{name}", cutter_mesh)
        cutter_obj.scale = (rad_x, rad_y, 1.0)
        # Position so it pierces through the upper wall (Z > 0)
        cutter_obj.location = (pos_x, 0.0, 0.010)
        bpy.context.scene.collection.objects.link(cutter_obj)
        cutter_obj.parent = ryuteki_root
        cutter_objs.append(cutter_obj)

        # Visible red inner rim / bevel border ring for the hole
        rim_mesh = bpy.data.meshes.new(f"Rim_{name}")
        r_verts = []
        r_faces = []
        segments = 24
        depth_rim = 0.0042
        r_out_factor = 1.06
        r_in_factor = 0.98
        
        for i in range(segments):
            th = 2.0 * math.pi * i / segments
            x_u = rad_x * math.cos(th)
            y_u = rad_y * math.sin(th)
            
            # Outer edge at flute surface
            curr_r = outer_r_mouth - ((pos_x - head_x) / length_x) * (outer_r_mouth - outer_r_tail)
            z_surf = math.sqrt(max(0.00001, curr_r * curr_r - y_u * y_u))
            
            # Outer upper vertex
            r_verts.append(Vector((x_u * r_out_factor, y_u * r_out_factor, z_surf + 0.0003)))
            # Inner lower vertex inside bore
            r_verts.append(Vector((x_u * r_in_factor, y_u * r_in_factor, inner_r - 0.0005)))
            
        for i in range(segments):
            nxt = (i + 1) % segments
            v0 = 2 * i
            v1 = 2 * i + 1
            v2 = 2 * nxt + 1
            v3 = 2 * nxt
            r_faces.append([v0, v1, v2, v3])
            
        rim_mesh.from_pydata(r_verts, [], r_faces)
        rim_mesh.update()
        rim_obj = bpy.data.objects.new(f"Rim_{name}", rim_mesh)
        rim_obj.data.materials.append(mat_inner_bore)
        rim_obj.location = (pos_x, 0, 0)
        bpy.context.scene.collection.objects.link(rim_obj)
        rim_obj.parent = ryuteki_root
        rim_collars.append(rim_obj)

    # Apply EXACT boolean difference modifiers for genuine inset holes
    for i, cutter in enumerate(cutter_objs):
        bool_mod = flute_obj.modifiers.new(name=f"Bool_Hole_{i}", type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.solver = 'EXACT'
        bool_mod.object = cutter
        # Hide cutter from render and viewport display
        cutter.display_type = 'WIRE'
        cutter.hide_render = True
        cutter.hide_viewport = True

    # -------------------------------------------------------------
    # 4. Traditional Wrapped Silk/Bark Bands (Kaba-maki)
    # The Ryuteki is heavily wrapped with thread/bark cords between
    # the tone holes and along the head/tail to reinforce the bamboo.
    # -------------------------------------------------------------
    binding_intervals = [
        # (Start X, End X, description)
        (-0.088, -0.060), # Head binding below crown
        (-0.045, -0.015), # Pre-embouchure wrapping
        ( 0.015,  0.092), # Between embouchure and hole 1
        ( 0.117,  0.119), # Spacing band
        ( 0.142,  0.144), # Spacing band
        ( 0.168,  0.170), # Spacing band
        ( 0.194,  0.196), # Spacing band
        ( 0.220,  0.222), # Spacing band
        ( 0.245,  0.247), # Spacing band
        ( 0.272,  0.306), # Foot binding near end
    ]

    for b_idx, (b_start, b_end) in enumerate(binding_intervals):
        b_len = b_end - b_start
        b_mid = (b_start + b_end) / 2.0
        u = (b_mid - head_x) / length_x
        rad_band = (outer_r_mouth - u * (outer_r_mouth - outer_r_tail)) + 0.0004
        
        b_mesh = bpy.data.meshes.new(f"WrappingBand_{b_idx}")
        b_verts = []
        b_faces = []
        b_steps = max(2, int(b_len * 400)) # thread ridges
        b_radial = 32
        
        for step in range(b_steps + 1):
            curr_x = b_start + (step / b_steps) * b_len
            # Slight wavy variation simulating individual thread windings
            ridge = 0.00015 * math.sin(step * math.pi)
            r = rad_band + ridge
            for s in range(b_radial):
                theta = 2.0 * math.pi * s / b_radial
                y = r * math.cos(theta)
                z = r * math.sin(theta)
                b_verts.append(Vector((curr_x, y, z)))
                
        for step in range(b_steps):
            st = step * b_radial
            nxt = (step + 1) * b_radial
            for s in range(b_radial):
                sn = (s + 1) % b_radial
                b_faces.append([st + s, nxt + s, nxt + sn, st + sn])
                
        b_mesh.from_pydata(b_verts, [], b_faces)
        b_mesh.update()
        band_obj = bpy.data.objects.new(f"WrappingBand_{b_idx}", b_mesh)
        band_obj.data.materials.append(mat_binding)
        bpy.context.scene.collection.objects.link(band_obj)
        band_obj.parent = ryuteki_root

    # -------------------------------------------------------------
    # 5. Head Construction (Kashira-gane, Lead Cork & Crown Ornament)
    # Ryuteki head houses a lead counterweight/cork (omoi) and ends in
    # a decorative metal cap (kashira-gane) with a silk knot/brocade.
    # -------------------------------------------------------------
    # Internal acoustic cork/plug situated just behind the blow hole
    plug_mesh = create_cylinder_mesh("InternalPlug", inner_r, inner_r, 0.025, radial_segments=24)
    plug_obj = bpy.data.objects.new("InternalPlug", plug_mesh)
    plug_obj.rotation_euler = (0, math.radians(90), 0)
    plug_obj.location = (-0.022, 0, 0)
    plug_obj.data.materials.append(mat_plug)
    bpy.context.scene.collection.objects.link(plug_obj)
    plug_obj.parent = ryuteki_root

    # Head metal ring fitting (Kashira-gane collar)
    head_collar_mesh = create_cylinder_mesh("HeadCollar", outer_r_mouth + 0.0006, outer_r_mouth + 0.0006, 0.006, radial_segments=36)
    head_collar = bpy.data.objects.new("HeadCollar", head_collar_mesh)
    head_collar.rotation_euler = (0, math.radians(90), 0)
    head_collar.location = (head_x + 0.002, 0, 0)
    head_collar.data.materials.append(mat_metal_fitting)
    bpy.context.scene.collection.objects.link(head_collar)
    head_collar.parent = ryuteki_root

    # Carved Wooden / Horn Crown Plug capping the head end
    crown_mesh = bpy.data.meshes.new("CrownPlug")
    cr_verts = []
    cr_faces = []
    cr_segs = 32
    cr_profiles = [
        (0.000, inner_r + 0.0015),
        (-0.004, outer_r_mouth + 0.0005),
        (-0.008, outer_r_mouth - 0.0010),
        (-0.012, 0.0090),
        (-0.015, 0.0060),
        (-0.017, 0.0010),
        (-0.018, 0.0000) # Tip center
    ]
    
    for x_off, r_val in cr_profiles[:-1]:
        for s in range(cr_segs):
            theta = 2.0 * math.pi * s / cr_segs
            y = r_val * math.cos(theta)
            z = r_val * math.sin(theta)
            cr_verts.append(Vector((head_x + x_off, y, z)))
            
    # Add tip vertex
    tip_v_idx = len(cr_verts)
    cr_verts.append(Vector((head_x + cr_profiles[-1][0], 0, 0)))
    
    # Rings faces
    num_prof = len(cr_profiles) - 1
    for p_idx in range(num_prof - 1):
        st = p_idx * cr_segs
        nxt = (p_idx + 1) * cr_segs
        for s in range(cr_segs):
            sn = (s + 1) % cr_segs
            cr_faces.append([st + s, st + sn, nxt + sn, nxt + s])
            
    # Cap to tip
    last_st = (num_prof - 1) * cr_segs
    for s in range(cr_segs):
        sn = (s + 1) % cr_segs
        cr_faces.append([last_st + s, last_st + sn, tip_v_idx])
        
    crown_mesh.from_pydata(cr_verts, [], cr_faces)
    crown_mesh.update()
    crown_obj = bpy.data.objects.new("CrownPlug", crown_mesh)
    crown_obj.data.materials.append(mat_outer_lacquer)
    bpy.context.scene.collection.objects.link(crown_obj)
    crown_obj.parent = ryuteki_root

    # Metal decorative end stud (Kanagu) at the crown
    stud_mesh = create_cylinder_mesh("HeadOrnamentStud", 0.004, 0.005, 0.005, radial_segments=20)
    stud_obj = bpy.data.objects.new("HeadOrnamentStud", stud_mesh)
    stud_obj.rotation_euler = (0, math.radians(90), 0)
    stud_obj.location = (head_x - 0.016, 0, 0)
    stud_obj.data.materials.append(mat_metal_fitting)
    bpy.context.scene.collection.objects.link(stud_obj)
    stud_obj.parent = ryuteki_root

    # -------------------------------------------------------------
    # 6. Silk Cord Knot Loop (Musubi cord through head stud)
    # -------------------------------------------------------------
    knot_mesh = bpy.data.meshes.new("TasselKnot")
    k_verts = []
    k_faces = []
    knot_steps = 36
    knot_rad = 0.0065
    tube_rad = 0.0014
    tube_segs = 8
    
    for i in range(knot_steps):
        phi = 2.0 * math.pi * i / knot_steps
        # Torus loop hanging vertically from the head
        cx = head_x - 0.021 + 0.002 * math.cos(phi)
        cy = 0.0
        cz = -knot_rad - 0.003 + knot_rad * math.sin(phi)
        
        # Local tangent along loop
        tangent = Vector((-0.002 * math.sin(phi), 0.0, knot_rad * math.cos(phi))).normalized()
        normal = Vector((0.0, 1.0, 0.0))
        binormal = tangent.cross(normal)
        
        for ts in range(tube_segs):
            psi = 2.0 * math.pi * ts / tube_segs
            offset = normal * (tube_rad * math.cos(psi)) + binormal * (tube_rad * math.sin(psi))
            k_verts.append(Vector((cx, cy, cz)) + offset)
            
    for i in range(knot_steps):
        nxt = (i + 1) % knot_steps
        st = i * tube_segs
        st_nxt = nxt * tube_segs
        for ts in range(tube_segs):
            ts_n = (ts + 1) % tube_segs
            k_faces.append([st + ts, st_nxt + ts, st_nxt + ts_n, st + ts_n])
            
    knot_mesh.from_pydata(k_verts, [], k_faces)
    knot_mesh.update()
    knot_obj = bpy.data.objects.new("TasselKnot", knot_mesh)
    knot_obj.data.materials.append(mat_tassel)
    bpy.context.scene.collection.objects.link(knot_obj)
    knot_obj.parent = ryuteki_root

    # Hanging tassel strands
    for side in (-0.002, 0.002):
        tassel_strand_mesh = create_cylinder_mesh(f"TasselStrand_{side}", 0.0011, 0.0006, 0.045, radial_segments=10)
        tassel_strand = bpy.data.objects.new(f"TasselStrand_{side}", tassel_strand_mesh)
        tassel_strand.location = (head_x - 0.021 + side, 0, -0.038)
        tassel_strand.rotation_euler = (math.radians(4 if side > 0 else -4), 0, 0)
        tassel_strand.data.materials.append(mat_tassel)
        bpy.context.scene.collection.objects.link(tassel_strand)
        tassel_strand.parent = ryuteki_root

    # -------------------------------------------------------------
    # 7. Foot End Fitting (Kanagu / Bone ring at bottom opening)
    # -------------------------------------------------------------
    foot_collar_mesh = create_cylinder_mesh("FootCollar", outer_r_tail + 0.0005, outer_r_tail + 0.0003, 0.005, radial_segments=32)
    foot_collar = bpy.data.objects.new("FootCollar", foot_collar_mesh)
    foot_collar.rotation_euler = (0, math.radians(90), 0)
    foot_collar.location = (foot_x - 0.0025, 0, 0)
    foot_collar.data.materials.append(mat_metal_fitting)
    bpy.context.scene.collection.objects.link(foot_collar)
    foot_collar.parent = ryuteki_root

    # -------------------------------------------------------------
    # 8. Decorative Presentation Pillow / Stand Rest (Kake-dai)
    # Enhances display of traditional Gagaku court instrument
    # -------------------------------------------------------------
    stand_mat = create_material("Ryuteki_StandLacquer", (0.015, 0.015, 0.018, 1.0), roughness=0.15)
    cushion_mat = create_material("Ryuteki_SilkCushion", (0.35, 0.03, 0.05, 1.0), roughness=0.6)

    # Base board
    base_mesh = bpy.data.meshes.new("StandBase")
    bw, bl, bh = 0.040, 0.320, 0.008
    b_verts = [
        Vector((-bl/2 + 0.11, -bw/2, -0.022)),
        Vector(( bl/2 + 0.11, -bw/2, -0.022)),
        Vector(( bl/2 + 0.11,  bw/2, -0.022)),
        Vector((-bl/2 + 0.11,  bw/2, -0.022)),
        Vector((-bl/2 + 0.11, -bw/2, -0.022 + bh)),
        Vector(( bl/2 + 0.11, -bw/2, -0.022 + bh)),
        Vector(( bl/2 + 0.11,  bw/2, -0.022 + bh)),
        Vector((-bl/2 + 0.11,  bw/2, -0.022 + bh))
    ]
    b_faces = [
        [0, 1, 2, 3], # Bottom
        [4, 7, 6, 5], # Top
        [0, 4, 5, 1], # Front
        [2, 6, 7, 3], # Back
        [0, 3, 7, 4], # Left
        [1, 5, 6, 2]  # Right
    ]
    base_mesh.from_pydata(b_verts, [], b_faces)
    base_mesh.update()
    stand_obj = bpy.data.objects.new("StandBase", base_mesh)
    stand_obj.data.materials.append(stand_mat)
    bpy.context.scene.collection.objects.link(stand_obj)
    stand_obj.parent = ryuteki_root

    # Two resting support pillars with concave saddles for the flute
    for p_x in (0.00, 0.22):
        pillar_mesh = bpy.data.meshes.new(f"RestPillar_{p_x}")
        pw, pl_p, ph = 0.026, 0.016, 0.018
        p_verts = [
            Vector((p_x - pl_p/2, -pw/2, -0.014)),
            Vector((p_x + pl_p/2, -pw/2, -0.014)),
            Vector((p_x + pl_p/2,  pw/2, -0.014)),
            Vector((p_x - pl_p/2,  pw/2, -0.014)),
            # Top points saddle-curved to cradle flute
            Vector((p_x - pl_p/2, -pw/2, -0.014 + ph)),
            Vector((p_x + pl_p/2, -pw/2, -0.014 + ph)),
            Vector((p_x + pl_p/2,  0,    -0.014 + ph - 0.004)),
            Vector((p_x - pl_p/2,  0,    -0.014 + ph - 0.004)),
            Vector((p_x + pl_p/2,  pw/2, -0.014 + ph)),
            Vector((p_x - pl_p/2,  pw/2, -0.014 + ph))
        ]
        p_faces = [
            [0, 1, 2, 3], # Bottom
            [4, 7, 6, 5], # Left top slope
            [7, 9, 8, 6], # Right top slope
            [0, 4, 5, 1], # Front
            [2, 8, 9, 3], # Back
            [0, 3, 9, 7, 4], # Left side
            [1, 5, 6, 8, 2]  # Right side
        ]
        pillar_mesh.from_pydata(p_verts, [], p_faces)
        pillar_mesh.update()
        p_obj = bpy.data.objects.new(f"RestPillar_{p_x}", pillar_mesh)
        p_obj.data.materials.append(cushion_mat)
        bpy.context.scene.collection.objects.link(p_obj)
        p_obj.parent = ryuteki_root

    return ryuteki_root

if __name__ == "__main__":
    build_model()
