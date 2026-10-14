"""
Procedural Japanese Chochin (Festival Lantern) Generator for Blender 5.2.
Constructs a traditional collapsible paper lantern with ribbing (higo),
crests/geometric ornaments, black lacquered collar rings, hanging loop,
suspension wire, bottom weight cap, and silk cord tassel.
"""

import math
import bpy
import mathutils


def create_workbench_material(name, rgba, roughness=0.4, metallic=0.0):
    """
    Creates or retrieves a material ensuring BOTH viewport Workbench diffuse_color
    and Principled BSDF Base Color are set to the exact same RGBA value.
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


def link_mesh_object(name, mesh, collection=None, parent=None):
    """Links a newly generated mesh to an object, scene collection, and optional parent."""
    obj = bpy.data.objects.new(name, mesh)
    if collection is None:
        collection = bpy.context.scene.collection
    collection.objects.link(obj)
    if parent is not None:
        obj.parent = parent
    return obj


def create_chochin_body(collection, mat_paper, mat_red, parent=None):
    """
    Generates the corrugated paper ribbed body of the chochin lantern
    with alternating or patterned geometric emblem bands/panels.
    """
    segments_radial = 36
    rings_v = 40  # Number of horizontal bamboo hoops (higo)
    height_total = 2.4
    r_max = 0.95
    r_rim = 0.44

    verts = []
    faces = []
    face_material_indices = []

    # Generate ring profile vertices with ribbed corrugation
    for iv in range(rings_v + 1):
        v_fac = iv / float(rings_v)  # 0.0 to 1.0 (bottom to top)
        z = -0.5 * height_total + v_fac * height_total

        # Barrel profile envelope: sin curve
        envelope = math.sin(v_fac * math.pi)
        base_r = r_rim + (r_max - r_rim) * math.pow(envelope, 0.72)

        # Micro-corrugation between hoops (subtle bamboo stave undulation)
        rib_wave = math.sin(v_fac * rings_v * math.pi)
        r = base_r + 0.016 * rib_wave

        for ir in range(segments_radial):
            theta = (ir / float(segments_radial)) * 2.0 * math.pi
            # Subtle facet bulging along circumference
            r_poly = r * (1.0 + 0.008 * math.cos(ir * 4))
            x = r_poly * math.cos(theta)
            y = r_poly * math.sin(theta)
            verts.append((x, y, z))

    # Build quad faces and assign paper vs decorative red emblem regions
    for iv in range(rings_v):
        v_norm = (iv + 0.5) / float(rings_v)
        is_mid_band = 0.28 <= v_norm <= 0.72

        for ir in range(segments_radial):
            ir_next = (ir + 1) % segments_radial
            v0 = iv * segments_radial + ir
            v1 = iv * segments_radial + ir_next
            v2 = (iv + 1) * segments_radial + ir_next
            v3 = (iv + 1) * segments_radial + ir

            faces.append((v0, v1, v2, v3))

            # Symmetrical stylized crest patterns / bold graphic panels
            # Quadrants centered at front (Y < 0, ir near 27) and back (Y > 0, ir near 9)
            # ir in [7..11] or [25..29]
            in_crest_ir = (7 <= ir <= 11) or (25 <= ir <= 29)
            # Additional horizontal top/bottom accent rings
            in_accent_ring = (iv == 4 or iv == 5 or iv == 34 or iv == 35)

            if (is_mid_band and in_crest_ir) or in_accent_ring:
                face_material_indices.append(1)  # mat_red
            else:
                face_material_indices.append(0)  # mat_paper

    mesh = bpy.data.meshes.new("Chochin_PaperBody_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    # Assign materials to slots
    mesh.materials.append(mat_paper)
    mesh.materials.append(mat_red)

    for i, poly in enumerate(mesh.polygons):
        poly.material_index = face_material_indices[i]
        poly.use_smooth = True

    obj = link_mesh_object("Chochin_PaperBody", mesh, collection=collection, parent=parent)
    return obj


def create_bamboo_ribs(collection, mat_ribs, parent=None):
    """
    Constructs the horizontal spiral/circular bamboo boning rings (higo)
    that physically give structure to the paper membrane.
    """
    hoop_count = 14
    height_total = 2.4
    r_max = 0.95
    r_rim = 0.44
    segments_radial = 32
    tube_facets = 4
    tube_radius = 0.012

    verts = []
    faces = []

    for ih in range(1, hoop_count):
        v_fac = ih / float(hoop_count)
        z_center = -0.5 * height_total + v_fac * height_total
        envelope = math.sin(v_fac * math.pi)
        r_center = (r_rim + (r_max - r_rim) * math.pow(envelope, 0.72)) + 0.008

        ring_start_index = len(verts)

        # Build toroidal hoop
        for iseg in range(segments_radial):
            theta = (iseg / float(segments_radial)) * 2.0 * math.pi
            cx = r_center * math.cos(theta)
            cy = r_center * math.sin(theta)

            # Local normal and binormal
            nx = math.cos(theta)
            ny = math.sin(theta)

            for itube in range(tube_facets):
                alpha = (itube / float(tube_facets)) * 2.0 * math.pi
                dx = tube_radius * math.cos(alpha) * nx
                dy = tube_radius * math.cos(alpha) * ny
                dz = tube_radius * math.sin(alpha)
                verts.append((cx + dx, cy + dy, z_center + dz))

        # Quad faces along the hoop
        for iseg in range(segments_radial):
            next_seg = (iseg + 1) % segments_radial
            for itube in range(tube_facets):
                next_tube = (itube + 1) % tube_facets
                i0 = ring_start_index + iseg * tube_facets + itube
                i1 = ring_start_index + next_seg * tube_facets + itube
                i2 = ring_start_index + next_seg * tube_facets + next_tube
                i3 = ring_start_index + iseg * tube_facets + next_tube
                faces.append((i0, i1, i2, i3))

    mesh = bpy.data.meshes.new("Chochin_Ribs_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    mesh.materials.append(mat_ribs)
    for p in mesh.polygons:
        p.use_smooth = True

    return link_mesh_object("Chochin_BambooRibs", mesh, collection=collection, parent=parent)


def create_rim_collar(name, z_center, r_outer, r_inner, height, collection, mat_lacquer, parent=None):
    """
    Constructs a thick, beveled black lacquered wooden collar (jibari rim)
    used for top aperture and bottom base.
    """
    segments = 36
    verts = []
    faces = []
    half_h = height * 0.5

    # 4 profile loops: inner-top, outer-top, outer-bottom, inner-bottom
    # with a slight chamfer contour
    r_out_mid = r_outer + 0.015

    for i in range(segments):
        th = (i / float(segments)) * 2.0 * math.pi
        ct = math.cos(th)
        st = math.sin(th)

        # 0: inner bottom
        verts.append((r_inner * ct, r_inner * st, z_center - half_h))
        # 1: outer bottom bevel
        verts.append((r_outer * ct, r_outer * st, z_center - half_h))
        # 2: outer mid crest
        verts.append((r_out_mid * ct, r_out_mid * st, z_center))
        # 3: outer top bevel
        verts.append((r_outer * ct, r_outer * st, z_center + half_h))
        # 4: inner top
        verts.append((r_inner * ct, r_inner * st, z_center + half_h))

    step = 5
    for i in range(segments):
        next_i = (i + 1) % segments
        b0 = i * step
        b1 = next_i * step

        # Inner-bottom to outer-bottom
        faces.append((b0 + 0, b1 + 0, b1 + 1, b0 + 1))
        # Outer-bottom to outer-mid
        faces.append((b0 + 1, b1 + 1, b1 + 2, b0 + 2))
        # Outer-mid to outer-top
        faces.append((b0 + 2, b1 + 2, b1 + 3, b0 + 3))
        # Outer-top to inner-top
        faces.append((b0 + 3, b1 + 3, b1 + 4, b0 + 4))
        # Inner-top to inner-bottom (interior wall)
        faces.append((b0 + 4, b1 + 4, b1 + 0, b0 + 0))

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    mesh.materials.append(mat_lacquer)
    for p in mesh.polygons:
        p.use_smooth = True

    return link_mesh_object(name, mesh, collection=collection, parent=parent)


def create_suspension_handle(collection, mat_lacquer, mat_metal, parent=None):
    """
    Creates the black wooden arch handle, brass hanging loop ring,
    and crossbars over the lantern top opening.
    """
    # 1. Wooden Cross Bar across top rim
    segments_bar = 8
    length = 0.84
    width = 0.05
    height = 0.04
    z_bar = 1.22

    # Cross beam vertices
    dx = width * 0.5
    dy = length * 0.5
    dz = height * 0.5

    bar_verts = [
        (-dx, -dy, z_bar - dz), (dx, -dy, z_bar - dz),
        (dx, dy, z_bar - dz), (-dx, dy, z_bar - dz),
        (-dx, -dy, z_bar + dz), (dx, -dy, z_bar + dz),
        (dx, dy, z_bar + dz), (-dx, dy, z_bar + dz)
    ]
    bar_faces = [
        (0, 1, 2, 3), (4, 7, 6, 5),
        (0, 4, 5, 1), (1, 5, 6, 2),
        (2, 6, 7, 3), (3, 7, 4, 0)
    ]
    bar_mesh = bpy.data.meshes.new("Chochin_TopBar_Mesh")
    bar_mesh.from_pydata(bar_verts, [], bar_faces)
    bar_mesh.update()
    bar_mesh.materials.append(mat_lacquer)
    link_mesh_object("Chochin_TopCrossBar", bar_mesh, collection=collection, parent=parent)

    # 2. Arch Handle
    arch_pts = 20
    arch_rad = 0.42
    arch_thickness = 0.02
    arch_verts = []
    arch_faces = []

    for i in range(arch_pts + 1):
        t = i / float(arch_pts)
        angle = t * math.pi  # 0 to PI
        cx = 0.0
        cy = -arch_rad * math.cos(angle)
        cz = z_bar + arch_rad * math.sin(angle) * 0.95

        # Profile circle
        for k in range(6):
            pk = (k / 6.0) * 2.0 * math.pi
            vx = arch_thickness * math.cos(pk)
            # normal in YZ plane
            norm_y = math.sin(angle)
            norm_z = math.cos(angle)
            vy = arch_thickness * math.sin(pk) * norm_y
            vz = arch_thickness * math.sin(pk) * norm_z
            arch_verts.append((cx + vx, cy + vy, cz + vz))

    for i in range(arch_pts):
        for k in range(6):
            k_next = (k + 1) % 6
            p0 = i * 6 + k
            p1 = (i + 1) * 6 + k
            p2 = (i + 1) * 6 + k_next
            p3 = i * 6 + k_next
            arch_faces.append((p0, p1, p2, p3))

    arch_mesh = bpy.data.meshes.new("Chochin_Arch_Mesh")
    arch_mesh.from_pydata(arch_verts, [], arch_faces)
    arch_mesh.update()
    arch_mesh.materials.append(mat_lacquer)
    for p in arch_mesh.polygons:
        p.use_smooth = True
    link_mesh_object("Chochin_ArchHandle", arch_mesh, collection=collection, parent=parent)

    # 3. Brass Ring Hook at apex of the arch
    z_apex = z_bar + arch_rad * 0.95 + 0.02
    ring_r = 0.09
    ring_tube = 0.014
    r_segs = 24
    t_segs = 8
    ring_verts = []
    ring_faces = []

    for i in range(r_segs):
        th = (i / float(r_segs)) * 2.0 * math.pi
        rcx = 0.0
        rcy = ring_r * math.cos(th)
        rcz = z_apex + ring_r + ring_r * math.sin(th)

        for j in range(t_segs):
            phi = (j / float(t_segs)) * 2.0 * math.pi
            vx = ring_tube * math.sin(phi)
            vy = ring_tube * math.cos(phi) * math.cos(th)
            vz = ring_tube * math.cos(phi) * math.sin(th)
            ring_verts.append((rcx + vx, rcy + vy, rcz + vz))

    for i in range(r_segs):
        next_i = (i + 1) % r_segs
        for j in range(t_segs):
            next_j = (j + 1) % t_segs
            p0 = i * t_segs + j
            p1 = next_i * t_segs + j
            p2 = next_i * t_segs + next_j
            p3 = i * t_segs + next_j
            ring_faces.append((p0, p1, p2, p3))

    ring_mesh = bpy.data.meshes.new("Chochin_HangingLoop_Mesh")
    ring_mesh.from_pydata(ring_verts, [], ring_faces)
    ring_mesh.update()
    ring_mesh.materials.append(mat_metal)
    for p in ring_mesh.polygons:
        p.use_smooth = True
    link_mesh_object("Chochin_HangingLoop", ring_mesh, collection=collection, parent=parent)


def create_bottom_assembly_and_tassel(collection, mat_lacquer, mat_metal, mat_tassel, mat_accent, parent=None):
    """
    Creates bottom weight cap, brass eyelet ring, ornamental knot/bead,
    and the cascading hanging silk fringe tassel (fusa).
    """
    z_bottom_collar = -1.22
    verts = []
    faces = []

    # 1. Conical bottom cap plug (black wood)
    cap_segs = 24
    cap_r_top = 0.38
    cap_r_bot = 0.12
    cap_depth = 0.12
    z_cap_top = z_bottom_collar
    z_cap_bot = z_cap_top - cap_depth

    for i in range(cap_segs):
        th = (i / float(cap_segs)) * 2.0 * math.pi
        ct = math.cos(th)
        st = math.sin(th)
        verts.append((cap_r_top * ct, cap_r_top * st, z_cap_top))
        verts.append((cap_r_bot * ct, cap_r_bot * st, z_cap_bot))

    for i in range(cap_segs):
        next_i = (i + 1) % cap_segs
        p0 = i * 2
        p1 = i * 2 + 1
        p2 = next_i * 2 + 1
        p3 = next_i * 2
        faces.append((p0, p1, p2, p3))

    # Base bottom cap disc
    center_idx = len(verts)
    verts.append((0.0, 0.0, z_cap_bot))
    for i in range(cap_segs):
        next_i = (i + 1) % cap_segs
        faces.append((i * 2 + 1, center_idx, next_i * 2 + 1))

    cap_mesh = bpy.data.meshes.new("Chochin_BottomCap_Mesh")
    cap_mesh.from_pydata(verts, [], faces)
    cap_mesh.update()
    cap_mesh.materials.append(mat_lacquer)
    for p in cap_mesh.polygons:
        p.use_smooth = True
    link_mesh_object("Chochin_BottomCap", cap_mesh, collection=collection, parent=parent)

    # 2. Brass eyelet ferrule under cap
    ferrule_verts = []
    ferrule_faces = []
    z_eyelet = z_cap_bot - 0.03
    f_r = 0.05
    f_h = 0.04
    for i in range(16):
        th = (i / 16.0) * 2.0 * math.pi
        ct = math.cos(th)
        st = math.sin(th)
        ferrule_verts.append((f_r * ct, f_r * st, z_eyelet + f_h * 0.5))
        ferrule_verts.append((f_r * ct, f_r * st, z_eyelet - f_h * 0.5))

    for i in range(16):
        next_i = (i + 1) % 16
        ferrule_faces.append((i * 2, i * 2 + 1, next_i * 2 + 1, next_i * 2))

    ferrule_mesh = bpy.data.meshes.new("Chochin_Ferrule_Mesh")
    ferrule_mesh.from_pydata(ferrule_verts, [], ferrule_faces)
    ferrule_mesh.update()
    ferrule_mesh.materials.append(mat_metal)
    for p in ferrule_mesh.polygons:
        p.use_smooth = True
    link_mesh_object("Chochin_Ferrule", ferrule_mesh, collection=collection, parent=parent)

    # 3. Agemaki ornamental cord knot & bead
    z_knot = z_eyelet - 0.10
    knot_mesh = bpy.data.meshes.new("Chochin_CordKnot_Mesh")
    k_verts = []
    k_faces = []
    # Decorative faceted bead (octahedral barrel)
    k_rad_max = 0.055
    k_rad_end = 0.02
    k_slices = 12
    k_levels = [-0.05, -0.015, 0.015, 0.05]
    k_radii = [k_rad_end, k_rad_max, k_rad_max, k_rad_end]

    for il, (zl, rl) in enumerate(zip(k_levels, k_radii)):
        for iseg in range(k_slices):
            th = (iseg / float(k_slices)) * 2.0 * math.pi
            k_verts.append((rl * math.cos(th), rl * math.sin(th), z_knot + zl))

    for il in range(3):
        for iseg in range(k_slices):
            next_seg = (iseg + 1) % k_slices
            p0 = il * k_slices + iseg
            p1 = il * k_slices + next_seg
            p2 = (il + 1) * k_slices + next_seg
            p3 = (il + 1) * k_slices + iseg
            k_faces.append((p0, p1, p2, p3))

    knot_mesh.from_pydata(k_verts, [], k_faces)
    knot_mesh.update()
    knot_mesh.materials.append(mat_accent)
    for p in knot_mesh.polygons:
        p.use_smooth = True
    link_mesh_object("Chochin_CordKnot", knot_mesh, collection=collection, parent=parent)

    # 4. Cascading Silk Fusa (Tassel Skirt + Core)
    z_tassel_head = z_knot - 0.06
    tassel_length = 0.65
    tassel_flares = 28
    t_verts = []
    t_faces = []

    # Flared bell skirt: 3 tiers of strands
    tiers = 6
    for it in range(tiers + 1):
        v_fac = it / float(tiers)
        zt = z_tassel_head - v_fac * tassel_length
        # Silk strands flare outwards slightly near the bottom
        rt = 0.038 + 0.075 * math.pow(v_fac, 1.4)

        for iseg in range(tassel_flares):
            th = (iseg / float(tassel_flares)) * 2.0 * math.pi
            # Subtle strand ripple
            wobble = 0.005 * math.sin(iseg * 3.0)
            t_verts.append(((rt + wobble) * math.cos(th), (rt + wobble) * math.sin(th), zt))

    for it in range(tiers):
        for iseg in range(tassel_flares):
            next_seg = (iseg + 1) % tassel_flares
            p0 = it * tassel_flares + iseg
            p1 = it * tassel_flares + next_seg
            p2 = (it + 1) * tassel_flares + next_seg
            p3 = (it + 1) * tassel_flares + iseg
            t_faces.append((p0, p1, p2, p3))

    # Inner tassel core volume to give solid thickness
    core_idx_start = len(t_verts)
    t_verts.append((0.0, 0.0, z_tassel_head))
    t_verts.append((0.0, 0.0, z_tassel_head - tassel_length))
    # Bottom closing cap
    bot_tier_start = tiers * tassel_flares
    for iseg in range(tassel_flares):
        next_seg = (iseg + 1) % tassel_flares
        t_faces.append((bot_tier_start + iseg, core_idx_start + 1, bot_tier_start + next_seg))

    tassel_mesh = bpy.data.meshes.new("Chochin_Tassel_Mesh")
    tassel_mesh.from_pydata(t_verts, [], t_faces)
    tassel_mesh.update()
    tassel_mesh.materials.append(mat_tassel)
    for p in tassel_mesh.polygons:
        p.use_smooth = True
    link_mesh_object("Chochin_SilkTassel", tassel_mesh, collection=collection, parent=parent)


def build_model():
    """
    Main builder entry point.
    Constructs an authentic Japanese Chochin lantern with high-contrast,
    Workbench-ready materials and detailed procedural geometry.
    """
    # 1. Setup Materials with identical diffuse_color & BSDF Base Color
    # Translucent warm washi paper
    mat_paper = create_workbench_material(
        name="Chochin_WashiPaper",
        rgba=(0.95, 0.91, 0.78, 1.0),
        roughness=0.6,
        metallic=0.0
    )
    # Saturated festival vermilion / crimson for emblems & panels
    mat_red = create_workbench_material(
        name="Chochin_Vermilion",
        rgba=(0.86, 0.12, 0.08, 1.0),
        roughness=0.4,
        metallic=0.0
    )
    # Pitch black lacquer for wood collars and arch
    mat_lacquer = create_workbench_material(
        name="Chochin_BlackLacquer",
        rgba=(0.04, 0.04, 0.04, 1.0),
        roughness=0.18,
        metallic=0.05
    )
    # Dark bamboo ribs
    mat_ribs = create_workbench_material(
        name="Chochin_BambooRibs",
        rgba=(0.35, 0.22, 0.12, 1.0),
        roughness=0.7,
        metallic=0.0
    )
    # Polished brass / gold fittings
    mat_brass = create_workbench_material(
        name="Chochin_BrassFittings",
        rgba=(0.92, 0.75, 0.25, 1.0),
        roughness=0.25,
        metallic=0.85
    )
    # Deep scarlet tassel silk
    mat_tassel = create_workbench_material(
        name="Chochin_SilkScarlet",
        rgba=(0.78, 0.05, 0.12, 1.0),
        roughness=0.5,
        metallic=0.0
    )
    # Golden yellow ornamental cord knot
    mat_knot = create_workbench_material(
        name="Chochin_GoldCord",
        rgba=(0.96, 0.68, 0.15, 1.0),
        roughness=0.35,
        metallic=0.1
    )

    # 2. Organize under a master root empty
    root_obj = bpy.data.objects.new("Japanese_Chochin_Lantern", None)
    root_obj.empty_display_type = 'PLAIN_AXES'
    root_obj.empty_display_size = 0.5
    bpy.context.scene.collection.objects.link(root_obj)

    col = bpy.context.scene.collection

    # 3. Create Chochin Ribbed Body with Red Crest Panels
    create_chochin_body(collection=col, mat_paper=mat_paper, mat_red=mat_red, parent=root_obj)

    # 4. Create Bamboo Rib Hoops
    create_bamboo_ribs(collection=col, mat_ribs=mat_ribs, parent=root_obj)

    # 5. Create Black Lacquered Rim Collars (Jibari)
    # Top rim
    create_rim_collar(
        name="Chochin_TopCollar",
        z_center=1.20,
        r_outer=0.48,
        r_inner=0.39,
        height=0.08,
        collection=col,
        mat_lacquer=mat_lacquer,
        parent=root_obj
    )
    # Bottom rim
    create_rim_collar(
        name="Chochin_BottomCollar",
        z_center=-1.20,
        r_outer=0.48,
        r_inner=0.39,
        height=0.08,
        collection=col,
        mat_lacquer=mat_lacquer,
        parent=root_obj
    )

    # 6. Suspension Handle, Brass Eyelet & Hanging Loop
    create_suspension_handle(
        collection=col,
        mat_lacquer=mat_lacquer,
        mat_metal=mat_brass,
        parent=root_obj
    )

    # 7. Bottom Cap, Cord Knot, and Silk Tassel
    create_bottom_assembly_and_tassel(
        collection=col,
        mat_lacquer=mat_lacquer,
        mat_metal=mat_brass,
        mat_tassel=mat_tassel,
        mat_accent=mat_knot,
        parent=root_obj
    )

    return root_obj
