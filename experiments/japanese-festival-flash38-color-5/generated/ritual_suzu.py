import bpy
import math
from mathutils import Vector, Matrix


def create_material(name, rgba, metallic=0.0, roughness=0.3):
    """Creates a material with matching Principled BSDF Base Color and diffuse_color for Workbench."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.diffuse_color = rgba

    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness

    return mat


def assign_material(obj, mat):
    """Assigns material to an object."""
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def make_bell_mesh(name, scale=0.035, gold_mat=None):
    """Constructs a detailed traditional Japanese suzu (spherical pellet bell) geometry with slit and loop."""
    verts = []
    faces = []

    # Suzu body: lat-long sphere profile with an open equatorial / bottom acoustic slit and bulging ridge
    num_lat = 10
    num_lon = 14
    r_equator = scale
    r_height = scale * 1.08

    # Generate rings of vertices
    for i in range(num_lat + 1):
        v = i / num_lat
        lat = (v - 0.5) * math.pi
        z = math.sin(lat) * r_height
        rad = math.cos(lat) * r_equator

        # Mid-band bulge (the characteristic equator rim ridge of suzu)
        if abs(lat) < 0.18:
            rad *= 1.15

        for j in range(num_lon):
            u = j / num_lon
            lon = u * 2.0 * math.pi
            x = math.cos(lon) * rad
            y = math.sin(lon) * rad
            verts.append((x, y, z))

    for i in range(num_lat):
        for j in range(num_lon):
            next_j = (j + 1) % num_lon
            # Omit bottom-front faces to mimic sound slit and cutout holes
            if i == 1 and (j in [0, 1, 7, 8]):
                continue
            v1 = i * num_lon + j
            v2 = (i + 1) * num_lon + j
            v3 = (i + 1) * num_lon + next_j
            v4 = i * num_lon + next_j
            faces.append((v1, v2, v3, v4))

    # Top attachment ring loop
    loop_segments = 8
    loop_radius = scale * 0.28
    loop_tube = scale * 0.07
    loop_base_idx = len(verts)
    loop_center_z = r_height + loop_radius * 0.7

    for a in range(loop_segments):
        theta = a * 2.0 * math.pi / loop_segments
        cz = loop_center_z + math.cos(theta) * loop_radius
        cx = math.sin(theta) * loop_radius
        for b in range(4):
            phi = b * 0.5 * math.pi
            offset_y = math.sin(phi) * loop_tube
            offset_radial = math.cos(phi) * loop_tube
            nx = cx + math.sin(theta) * offset_radial
            nz = cz + math.cos(theta) * offset_radial
            verts.append((nx, offset_y, nz))

    for a in range(loop_segments):
        next_a = (a + 1) % loop_segments
        for b in range(4):
            next_b = (b + 1) % 4
            v1 = loop_base_idx + a * 4 + b
            v2 = loop_base_idx + next_a * 4 + b
            v3 = loop_base_idx + next_a * 4 + next_b
            v4 = loop_base_idx + a * 4 + next_b
            faces.append((v1, v2, v3, v4))

    mesh = bpy.data.meshes.new(name=name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name=name, object_data=mesh)
    bpy.context.collection.objects.link(obj)
    if gold_mat:
        assign_material(obj, gold_mat)

    return obj


def make_torus_ring(name, major_r, minor_r, segments_u=24, segments_v=8, mat=None):
    """Procedurally builds a smooth torus ring for tiered suzu mounting frames."""
    verts = []
    faces = []

    for i in range(segments_u):
        u = i * 2.0 * math.pi / segments_u
        cu = math.cos(u)
        su = math.sin(u)
        cx = cu * major_r
        cy = su * major_r

        for j in range(segments_v):
            v = j * 2.0 * math.pi / segments_v
            cv = math.cos(v)
            sv = math.sin(v)
            px = (major_r + minor_r * cv) * cu
            py = (major_r + minor_r * cv) * su
            pz = minor_r * sv
            verts.append((px, py, pz))

    for i in range(segments_u):
        next_i = (i + 1) % segments_u
        for j in range(segments_v):
            next_j = (j + 1) % segments_v
            v1 = i * segments_v + j
            v2 = next_i * segments_v + j
            v3 = next_i * segments_v + next_j
            v4 = i * segments_v + next_j
            faces.append((v1, v2, v3, v4))

    mesh = bpy.data.meshes.new(name=name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name=name, object_data=mesh)
    bpy.context.collection.objects.link(obj)
    if mat:
        assign_material(obj, mat)

    return obj


def make_curved_spoke(name, start_p, end_p, sag_dir, sag_amount, radius, segments=10, mat=None):
    """Creates a gentle arching branch spoke between central staff and tier ring."""
    verts = []
    faces = []

    points = []
    for s in range(segments + 1):
        t = s / segments
        pt = start_p.lerp(end_p, t)
        sag = 4.0 * t * (1.0 - t) * sag_amount
        pt = pt + sag_dir * sag
        points.append(pt)

    radial_divs = 6
    for idx, pt in enumerate(points):
        if idx < segments:
            tangent = (points[idx + 1] - pt).normalized()
        else:
            tangent = (pt - points[idx - 1]).normalized()

        up = Vector((0.0, 0.0, 1.0))
        if abs(tangent.dot(up)) > 0.95:
            up = Vector((0.0, 1.0, 0.0))
        normal = tangent.cross(up).normalized()
        binormal = tangent.cross(normal).normalized()

        for k in range(radial_divs):
            angle = k * 2.0 * math.pi / radial_divs
            offset = (normal * math.cos(angle) + binormal * math.sin(angle)) * radius
            verts.append(pt + offset)

    for i in range(segments):
        for k in range(radial_divs):
            next_k = (k + 1) % radial_divs
            v1 = i * radial_divs + k
            v2 = (i + 1) * radial_divs + k
            v3 = (i + 1) * radial_divs + next_k
            v4 = i * radial_divs + next_k
            faces.append((v1, v2, v3, v4))

    mesh = bpy.data.meshes.new(name=name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name=name, object_data=mesh)
    bpy.context.collection.objects.link(obj)
    if mat:
        assign_material(obj, mat)

    return obj


def make_cylinder_section(name, r_bottom, r_top, height, z_offset=0.0, segments=20, mat=None):
    """Creates a capped conical cylinder section."""
    verts = []
    faces = []

    # Bottom ring
    for i in range(segments):
        th = i * 2.0 * math.pi / segments
        verts.append((r_bottom * math.cos(th), r_bottom * math.sin(th), z_offset))
    # Top ring
    for i in range(segments):
        th = i * 2.0 * math.pi / segments
        verts.append((r_top * math.cos(th), r_top * math.sin(th), z_offset + height))

    # Side faces
    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append((i, next_i, segments + next_i, segments + i))

    # Caps
    bottom_center = len(verts)
    verts.append((0.0, 0.0, z_offset))
    top_center = len(verts)
    verts.append((0.0, 0.0, z_offset + height))

    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append((bottom_center, next_i, i))
        faces.append((top_center, segments + i, segments + next_i))

    mesh = bpy.data.meshes.new(name=name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name=name, object_data=mesh)
    bpy.context.collection.objects.link(obj)
    if mat:
        assign_material(obj, mat)

    return obj


def make_ribbon(name, start_pos, length, width, ribbon_color):
    """Creates a flowing double-faced Shinto five-colored streamer ribbon with realistic natural drape."""
    verts = []
    faces = []
    num_steps = 22
    step_len = length / num_steps

    # Generate snake-like wavy path downward with gentle flare
    path = []
    curr = Vector(start_pos)
    phase_offset = (start_pos[0] * 5.0 + start_pos[1] * 7.0)

    for i in range(num_steps + 1):
        t = i / num_steps
        sway_x = math.sin(t * 5.0 + phase_offset) * (0.015 + t * 0.04)
        sway_y = math.cos(t * 4.5 + phase_offset) * (0.015 + t * 0.04)
        drop_z = -math.pow(t, 0.95) * length
        pos = Vector((curr.x + sway_x, curr.y + sway_y, curr.z + drop_z))
        path.append(pos)

    # Generate ribbon strip along path
    for i in range(num_steps + 1):
        pt = path[i]
        if i < num_steps:
            tangent = (path[i + 1] - pt).normalized()
        else:
            tangent = (pt - path[i - 1]).normalized()

        cross_dir = tangent.cross(Vector((0.0, 0.0, 1.0)))
        if cross_dir.length < 0.01:
            cross_dir = Vector((1.0, 0.0, 0.0))
        else:
            cross_dir.normalize()

        half_w = (width * 0.5) * (1.0 + 0.25 * math.sin(i * 0.4))
        p1 = pt - cross_dir * half_w
        p2 = pt + cross_dir * half_w
        verts.append(p1)
        verts.append(p2)

    for i in range(num_steps):
        v1 = i * 2
        v2 = v1 + 1
        v3 = (i + 1) * 2 + 1
        v4 = (i + 1) * 2
        faces.append((v1, v2, v3, v4))
        # Reverse face for double sided rendering
        faces.append((v1, v4, v3, v2))

    mesh = bpy.data.meshes.new(name=name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name=name, object_data=mesh)
    bpy.context.collection.objects.link(obj)
    assign_material(obj, ribbon_color)

    return obj


def build_model():
    """Builds a complete, detailed Kagura Suzu wand model."""
    # Palette definition adhering to strict Workbench Diffuse + Principled Base Color requirement
    gold_mat = create_material("Kagura_PolishedGold", (0.95, 0.76, 0.18, 1.0), metallic=0.92, roughness=0.18)
    bronze_gold = create_material("Kagura_DarkGold", (0.80, 0.58, 0.12, 1.0), metallic=0.88, roughness=0.25)
    red_lacquer = create_material("Kagura_RedLacquer", (0.82, 0.06, 0.06, 1.0), metallic=0.05, roughness=0.15)
    ivory_wrap = create_material("Kagura_IvoryWrap", (0.96, 0.93, 0.85, 1.0), metallic=0.0, roughness=0.6)
    dark_cord = create_material("Kagura_SilkRedCord", (0.55, 0.03, 0.03, 1.0), metallic=0.0, roughness=0.45)

    # Traditional Shinto Goshikiban 5 ribbon colors (Green, Red, Yellow, White, Purple/Blue)
    mat_rib_green = create_material("Ribbon_Green", (0.05, 0.65, 0.22, 1.0), roughness=0.4)
    mat_rib_red = create_material("Ribbon_Red", (0.88, 0.08, 0.08, 1.0), roughness=0.4)
    mat_rib_yellow = create_material("Ribbon_Yellow", (0.98, 0.82, 0.10, 1.0), roughness=0.4)
    mat_rib_white = create_material("Ribbon_White", (0.95, 0.95, 0.95, 1.0), roughness=0.4)
    mat_rib_purple = create_material("Ribbon_Purple", (0.42, 0.12, 0.68, 1.0), roughness=0.4)

    root_obj = bpy.data.objects.new("Kagura_Suzu_Root", None)
    bpy.context.collection.objects.link(root_obj)

    # =========================================================================
    # 1. LOWER HANDLE & HILT (Lacquered Wood & Wrapping)
    # =========================================================================
    # Butt cap (Kashira - polished gold pommel)
    pommel = make_cylinder_section("Kashira_Pommel", 0.016, 0.019, 0.024, z_offset=-0.26, segments=20, mat=gold_mat)
    pommel.parent = root_obj

    pommel_ball = make_cylinder_section("Kashira_RingMount", 0.007, 0.007, 0.018, z_offset=-0.278, segments=12, mat=gold_mat)
    pommel_ball.parent = root_obj

    # Main red lacquered grip
    handle = make_cylinder_section("Handle_WoodGrip", 0.017, 0.016, 0.20, z_offset=-0.24, segments=24, mat=red_lacquer)
    handle.parent = root_obj

    # Decorative spiral diamond-wrapped handle bands (Ivory and Red tsuka-ito)
    wrap_turns = 14
    wrap_steps = 70
    wrap_verts = []
    wrap_faces = []
    wrap_thick = 0.0016
    wrap_width = 0.009

    for w in range(wrap_steps):
        t = w / (wrap_steps - 1)
        z = -0.23 + t * 0.18
        theta = t * wrap_turns * math.pi
        r = 0.0168
        bx = math.cos(theta) * r
        by = math.sin(theta) * r
        tangent = Vector((-math.sin(theta), math.cos(theta), 0.1)).normalized()
        norm = Vector((bx, by, 0.0)).normalized()

        wrap_verts.append((bx - norm.x * wrap_thick, by - norm.y * wrap_thick, z - wrap_width * 0.5))
        wrap_verts.append((bx + norm.x * wrap_thick, by + norm.y * wrap_thick, z + wrap_width * 0.5))

    for w in range(wrap_steps - 1):
        v1 = w * 2
        v2 = v1 + 1
        v3 = (w + 1) * 2 + 1
        v4 = (w + 1) * 2
        wrap_faces.append((v1, v2, v3, v4))
        wrap_faces.append((v1, v4, v3, v2))

    wrap_mesh = bpy.data.meshes.new("Handle_IvoryLacing_mesh")
    wrap_mesh.from_pydata(wrap_verts, [], wrap_faces)
    wrap_mesh.update()
    wrap_obj = bpy.data.objects.new("Handle_IvoryLacing", wrap_mesh)
    bpy.context.collection.objects.link(wrap_obj)
    assign_material(wrap_obj, ivory_wrap)
    wrap_obj.parent = root_obj

    # Collar / Fuchi brass separator above handle
    collar = make_cylinder_section("Handle_GoldCollar", 0.019, 0.018, 0.022, z_offset=-0.04, segments=24, mat=gold_mat)
    collar.parent = root_obj

    # Lower ribbon tie ring / collar ferrule
    ribbon_ferrule = make_torus_ring("Ribbon_AnchorRing", 0.0195, 0.004, segments_u=20, segments_v=8, mat=dark_cord)
    ribbon_ferrule.location = Vector((0.0, 0.0, -0.042))
    ribbon_ferrule.parent = root_obj

    # =========================================================================
    # 2. CENTRAL SHAFT & TIERED ARBOR
    # =========================================================================
    # Main golden vertical stem
    stem = make_cylinder_section("Staff_CentralSpindle", 0.011, 0.008, 0.44, z_offset=-0.02, segments=20, mat=gold_mat)
    stem.parent = root_obj

    # Crown spire / top ornamental finial (Houju jewel & lotus pedestal)
    spire_base = make_cylinder_section("Spire_LotusBase", 0.014, 0.009, 0.025, z_offset=0.42, segments=18, mat=gold_mat)
    spire_base.parent = root_obj

    spire_finial = make_bell_mesh("Finial_CrownSuzu", scale=0.038, gold_mat=gold_mat)
    spire_finial.location = Vector((0.0, 0.0, 0.455))
    spire_finial.parent = root_obj

    # =========================================================================
    # 3. THREE TIERS OF SUZU BELLS (Traditional 7-5-3 configuration = 15 bells total)
    # =========================================================================
    # Tier 1 (Bottom tier): 7 bells, largest outward ring
    # Tier 2 (Middle tier): 5 bells, medium ring
    # Tier 3 (Top tier): 3 bells, compact ring
    tiers_info = [
        {"name": "Tier_Bottom_7Bells", "z": 0.08, "ring_r": 0.095, "spokes": 7, "bell_count": 7, "bell_sz": 0.029, "angle_offset": 0.0},
        {"name": "Tier_Middle_5Bells", "z": 0.22, "ring_r": 0.075, "spokes": 5, "bell_count": 5, "bell_sz": 0.027, "angle_offset": 0.35},
        {"name": "Tier_Top_3Bells", "z": 0.34, "ring_r": 0.052, "spokes": 3, "bell_count": 3, "bell_sz": 0.025, "angle_offset": 0.70},
    ]

    for tier_idx, tinfo in enumerate(tiers_info):
        tz = tinfo["z"]
        rr = tinfo["ring_r"]
        count = tinfo["bell_count"]
        b_scale = tinfo["bell_sz"]
        ang_off = tinfo["angle_offset"]

        # Hub disk on shaft
        hub = make_cylinder_section(f"Hub_{tier_idx+1}", 0.0135, 0.0135, 0.012, z_offset=tz - 0.006, segments=18, mat=gold_mat)
        hub.parent = root_obj

        # Circumferential mounting ring
        ring = make_torus_ring(f"Ring_Frame_{tier_idx+1}", rr, 0.0035, segments_u=28, segments_v=8, mat=gold_mat)
        ring.location = Vector((0.0, 0.0, tz))
        ring.parent = root_obj

        # Radiating curved branches / spokes
        for k in range(count):
            angle = ang_off + k * 2.0 * math.pi / count
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)

            # Start point at hub, end point at ring
            p_start = Vector((cos_a * 0.013, sin_a * 0.013, tz))
            p_end = Vector((cos_a * rr, sin_a * rr, tz))
            sag_dir = Vector((0.0, 0.0, -1.0))
            spoke = make_curved_spoke(
                f"Spoke_T{tier_idx+1}_{k+1}",
                p_start,
                p_end,
                sag_dir,
                sag_amount=0.012,
                radius=0.003,
                segments=8,
                mat=gold_mat,
            )
            spoke.parent = root_obj

            # Suspension clevis / loop link connecting bell to frame
            link = make_torus_ring(f"Link_T{tier_idx+1}_{k+1}", 0.007, 0.0016, segments_u=12, segments_v=6, mat=bronze_gold)
            link.location = Vector((cos_a * rr, sin_a * rr, tz - 0.008))
            link.rotation_euler = (0.0, math.pi * 0.5, angle)
            link.parent = root_obj

            # Golden Suzu bell hanging outward/downward from ring edge
            bell = make_bell_mesh(f"Suzu_T{tier_idx+1}_{k+1}", scale=b_scale, gold_mat=gold_mat)
            bell_drop_z = tz - 0.008 - (b_scale * 1.08)
            bell.location = Vector((cos_a * (rr + 0.004), sin_a * (rr + 0.004), bell_drop_z))

            # Slight outward flare angle for natural kinetic ritual appearance
            bell.rotation_euler = (sin_a * 0.22, -cos_a * 0.22, angle)
            bell.parent = root_obj

    # =========================================================================
    # 4. FIVE-COLORED STREAMER RIBBONS (Goshiki-no-suzu / Goshikiban)
    # =========================================================================
    ribbon_configs = [
        {"name": "Ribbon_Green", "color": mat_rib_green, "angle": 0.0 * math.pi, "len": 0.44},
        {"name": "Ribbon_Red", "color": mat_rib_red, "angle": 0.4 * math.pi, "len": 0.46},
        {"name": "Ribbon_Yellow", "color": mat_rib_yellow, "angle": 0.8 * math.pi, "len": 0.48},
        {"name": "Ribbon_White", "color": mat_rib_white, "angle": 1.2 * math.pi, "len": 0.45},
        {"name": "Ribbon_Purple", "color": mat_rib_purple, "angle": 1.6 * math.pi, "len": 0.47},
    ]

    ferrule_r = 0.021
    ferrule_z = -0.042

    for rinfo in ribbon_configs:
        ang = rinfo["angle"]
        start_pt = (math.cos(ang) * ferrule_r, math.sin(ang) * ferrule_r, ferrule_z)
        rib = make_ribbon(
            rinfo["name"],
            start_pos=start_pt,
            length=rinfo["len"],
            width=0.022,
            ribbon_color=rinfo["color"],
        )
        rib.parent = root_obj

    # Bottom tassel silk knot at base of handle
    pommel_tassel_ring = make_torus_ring("Pommel_KnotRing", 0.012, 0.003, segments_u=16, segments_v=6, mat=dark_cord)
    pommel_tassel_ring.location = Vector((0.0, 0.0, -0.282))
    pommel_tassel_ring.rotation_euler = (math.pi * 0.5, 0.0, 0.0)
    pommel_tassel_ring.parent = root_obj

    # Twin red silk cord tails dangling below pommel
    cord_1 = make_ribbon("Pommel_SilkCord_1", (0.004, 0.0, -0.285), 0.14, 0.007, dark_cord)
    cord_1.parent = root_obj
    cord_2 = make_ribbon("Pommel_SilkCord_2", (-0.004, 0.0, -0.285), 0.13, 0.007, dark_cord)
    cord_2.parent = root_obj

    return root_obj
