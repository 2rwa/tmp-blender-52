import bpy
import math
from mathutils import Vector, Matrix


def create_material(name, base_color, metallic=0.0, roughness=0.4, clearcoat=0.0):
    """Creates a Principled BSDF material compatible with Blender 5.x."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = base_color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if "Clearcoat Weight" in bsdf.inputs:
            bsdf.inputs["Clearcoat Weight"].default_value = clearcoat
        elif "Clearcoat" in bsdf.inputs:
            bsdf.inputs["Clearcoat"].default_value = clearcoat
    return mat


def create_mesh_object(name, verts, faces, material=None):
    """Creates a mesh and links it to the active collection."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    # Enable smooth shading for organic and curved metal surfaces
    for poly in mesh.polygons:
        poly.use_smooth = True
        
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    if material:
        obj.data.materials.append(material)
        
    return obj


def create_revolved_mesh(name, profile_points, radial_segments=32, material=None):
    """
    Revolves a 2D profile (list of (x, z) points) around the Z axis.
    Normal pointing rules follow standard sweep order.
    """
    verts = []
    num_pts = len(profile_points)
    
    for pt_idx, (r, z) in enumerate(profile_points):
        for s in range(radial_segments):
            theta = 2.0 * math.pi * s / radial_segments
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            verts.append((x, y, z))
            
    faces = []
    for i in range(num_pts - 1):
        for s in range(radial_segments):
            next_s = (s + 1) % radial_segments
            v1 = i * radial_segments + s
            v2 = i * radial_segments + next_s
            v3 = (i + 1) * radial_segments + next_s
            v4 = (i + 1) * radial_segments + s
            faces.append((v1, v2, v3, v4))
            
    return create_mesh_object(name, verts, faces, material=material)


def build_bamboo_stem(mat_bamboo):
    """
    Constructs the slender central bamboo stem (raos) with characteristic nodes,
    inter-nodal tapering, and slight bamboo ridge swelling.
    Stem aligned along Y axis, centered near origin.
    Length ~ 150mm, base radius ~ 3.8mm.
    """
    radial_segs = 24
    num_slices = 55
    y_min = -70.0
    y_max = 70.0
    
    # 2 visible bamboo nodes along the length
    node1_y = -22.0
    node2_y = 25.0
    
    verts = []
    for i in range(num_slices):
        t = i / (num_slices - 1)
        y = y_min + t * (y_max - y_min)
        
        # Subtle gentle taper from mouthpiece end to bowl end
        base_r = 3.6 + 0.3 * (1.0 - t)
        
        # Swell at nodes
        d1 = abs(y - node1_y)
        d2 = abs(y - node2_y)
        w1 = math.exp(-(d1 ** 2) / 3.5)
        w2 = math.exp(-(d2 ** 2) / 3.5)
        node_swell = (w1 + w2) * 0.45
        
        # Subtle ring lip groove near nodes
        lip1 = math.exp(-((d1 - 1.2) ** 2) / 0.8) * 0.22
        lip2 = math.exp(-((d2 - 1.2) ** 2) / 0.8) * 0.22
        
        r = base_r + node_swell + lip1 + lip2
        
        for s in range(radial_segs):
            theta = 2.0 * math.pi * s / radial_segs
            # Slight non-circular organic bamboo cross-section
            organic_var = 1.0 + 0.02 * math.cos(2.0 * theta) + 0.015 * math.sin(3.0 * theta)
            cur_r = r * organic_var
            x = cur_r * math.cos(theta)
            z = cur_r * math.sin(theta)
            verts.append((x, y, z))
            
    faces = []
    for i in range(num_slices - 1):
        for s in range(radial_segs):
            next_s = (s + 1) % radial_segs
            v1 = i * radial_segs + s
            v2 = i * radial_segs + next_s
            v3 = (i + 1) * radial_segs + next_s
            v4 = (i + 1) * radial_segs + s
            faces.append((v1, v4, v3, v2))
            
    return create_mesh_object("BambooStem_Raos", verts, faces, mat_bamboo)


def build_fitting_ferrule(name, y_offset, direction, mat_brass):
    """
    Constructs an engraved decorative brass joining collar / ferrule
    between the bamboo stem and metal ends.
    direction: +1 for bowl side (+Y), -1 for mouthpiece side (-Y)
    """
    radial_segs = 32
    # Ferrule profile along local Y
    # Radius profiles with molded rings and engravings
    profile = [
        (3.85, 0.0),
        (4.25, 1.0 * direction),
        (4.45, 2.5 * direction),
        (4.25, 3.2 * direction),
        (4.35, 4.0 * direction),
        (4.15, 5.0 * direction),
        (3.95, 6.5 * direction),
    ]
    
    verts = []
    for r, local_y in profile:
        abs_y = y_offset + local_y
        for s in range(radial_segs):
            theta = 2.0 * math.pi * s / radial_segs
            # Fine 16-facet engraved reeding relief
            engraving = 0.04 * math.sin(16.0 * theta)
            cur_r = r + engraving
            x = cur_r * math.cos(theta)
            z = cur_r * math.sin(theta)
            verts.append((x, abs_y, z))
            
    faces = []
    num_rings = len(profile)
    for i in range(num_rings - 1):
        for s in range(radial_segs):
            next_s = (s + 1) % radial_segs
            v1 = i * radial_segs + s
            v2 = i * radial_segs + next_s
            v3 = (i + 1) * radial_segs + next_s
            v4 = (i + 1) * radial_segs + s
            if direction > 0:
                faces.append((v1, v4, v3, v2))
            else:
                faces.append((v1, v2, v3, v4))
                
    return create_mesh_object(name, verts, faces, mat_brass)


def build_mouthpiece(mat_silver):
    """
    Constructs the traditional metal mouthpiece (suikuchi),
    extending backwards along -Y from y = -76.5 to ~ -125.0 mm.
    Features subtle flattening near tip for lips and a smoke draw bore.
    """
    radial_segs = 28
    slices = [
        # (y, rx, rz)
        (-76.5,  3.90, 3.90),
        (-80.0,  3.85, 3.85),
        (-90.0,  3.60, 3.60),
        (-102.0, 3.35, 3.30),
        (-112.0, 3.10, 2.85),
        (-118.0, 2.90, 2.30),
        (-123.0, 2.80, 1.85),
        (-125.0, 2.70, 1.65),  # Lip resting tip
        (-125.5, 2.50, 1.50),  # Rounded end edge
    ]
    
    verts = []
    for y, rx, rz in slices:
        for s in range(radial_segs):
            theta = 2.0 * math.pi * s / radial_segs
            x = rx * math.cos(theta)
            z = rz * math.sin(theta)
            verts.append((x, y, z))
            
    faces = []
    num_rings = len(slices)
    for i in range(num_rings - 1):
        for s in range(radial_segs):
            next_s = (s + 1) % radial_segs
            v1 = i * radial_segs + s
            v2 = i * radial_segs + next_s
            v3 = (i + 1) * radial_segs + next_s
            v4 = (i + 1) * radial_segs + s
            faces.append((v1, v2, v3, v4))
            
    # Open suction aperture / bore at tip
    inner_rx, inner_rz = 1.0, 0.7
    bore_start_idx = len(verts)
    bore_y = -125.5
    for s in range(radial_segs):
        theta = 2.0 * math.pi * s / radial_segs
        x = inner_rx * math.cos(theta)
        z = inner_rz * math.sin(theta)
        verts.append((x, bore_y, z))
        
    # Cap between outer tip and bore rim
    last_ring_idx = (num_rings - 1) * radial_segs
    for s in range(radial_segs):
        next_s = (s + 1) % radial_segs
        o1 = last_ring_idx + s
        o2 = last_ring_idx + next_s
        i2 = bore_start_idx + next_s
        i1 = bore_start_idx + s
        faces.append((o1, o2, i2, i1))
        
    # Internal hollow cavity cylinder (recess into mouthpiece)
    cavity_depth_y = -118.0
    cavity_deep_idx = len(verts)
    for s in range(radial_segs):
        theta = 2.0 * math.pi * s / radial_segs
        x = inner_rx * 0.9 * math.cos(theta)
        z = inner_rz * 0.9 * math.sin(theta)
        verts.append((x, cavity_depth_y, z))
        
    for s in range(radial_segs):
        next_s = (s + 1) % radial_segs
        f1 = bore_start_idx + s
        f2 = bore_start_idx + next_s
        f3 = cavity_deep_idx + next_s
        f4 = cavity_deep_idx + s
        faces.append((f1, f4, f3, f2))
        
    # Center cap of deep cavity
    cavity_cap_center = (0.0, cavity_depth_y, 0.0)
    c_idx = len(verts)
    verts.append(cavity_cap_center)
    for s in range(radial_segs):
        next_s = (s + 1) % radial_segs
        faces.append((c_idx, cavity_deep_idx + s, cavity_deep_idx + next_s))
        
    return create_mesh_object("Mouthpiece_Suikuchi", verts, faces, mat_silver)


def build_gooseneck_and_heel(mat_silver):
    """
    Constructs the curving neck (gankubi) leading forward from y = +76.5,
    forming the sweep into the upward-pointing bowl pedestal, and the traditional
    protective heel/spur (kiseru-jiri) at the bottom.
    """
    radial_segs = 24
    
    # Spine path through 3D space: (Center Position, Normal Vector, Radius)
    # The pipe starts horizontal along +Y, curves upward into +Z.
    path_def = [
        # (x, y, z, tangent_dir, radius)
        (0.0,  76.5,  0.0, Vector((0.0, 1.0, 0.0)),  3.90),
        (0.0,  83.0,  0.0, Vector((0.0, 1.0, 0.0)),  3.70),
        (0.0,  92.0,  0.0, Vector((0.0, 1.0, 0.0)),  3.40),
        (0.0, 101.0,  0.2, Vector((0.0, 1.0, 0.15)), 3.10),
        (0.0, 108.0,  0.8, Vector((0.0, 0.95, 0.3)), 2.85),
        (0.0, 114.0,  2.2, Vector((0.0, 0.82, 0.57)), 2.65),
        (0.0, 118.5,  4.6, Vector((0.0, 0.60, 0.80)), 2.50),
        (0.0, 121.2,  8.0, Vector((0.0, 0.35, 0.94)), 2.45),
        (0.0, 122.2, 12.0, Vector((0.0, 0.05, 1.00)), 2.45),
        (0.0, 122.2, 14.5, Vector((0.0, 0.00, 1.00)), 2.60),  # Bowl seat transition
    ]
    
    verts = []
    for px, py, pz, tdir, r in path_def:
        tangent = tdir.normalized()
        # Binormal and normal for cross section
        right = Vector((1.0, 0.0, 0.0))
        up = tangent.cross(right).normalized()
        
        for s in range(radial_segs):
            theta = 2.0 * math.pi * s / radial_segs
            offset = right * (math.cos(theta) * r) + up * (math.sin(theta) * r)
            pt = Vector((px, py, pz)) + offset
            verts.append((pt.x, pt.y, pt.z))
            
    faces = []
    num_rings = len(path_def)
    for i in range(num_rings - 1):
        for s in range(radial_segs):
            next_s = (s + 1) % radial_segs
            v1 = i * radial_segs + s
            v2 = i * radial_segs + next_s
            v3 = (i + 1) * radial_segs + next_s
            v4 = (i + 1) * radial_segs + s
            faces.append((v1, v4, v3, v2))
            
    # Add the traditional resting spur/heel at the bottom of the bend
    heel_start_idx = len(verts)
    heel_center = Vector((0.0, 115.5, -0.6))
    heel_radius = 2.2
    heel_depth = 1.6
    
    for s in range(radial_segs):
        theta = 2.0 * math.pi * s / radial_segs
        hx = heel_radius * math.cos(theta)
        hy = 115.5 + heel_radius * 0.7 * math.sin(theta)
        hz = 0.2
        verts.append((hx, hy, hz))
        
    heel_rim_idx = len(verts)
    for s in range(radial_segs):
        theta = 2.0 * math.pi * s / radial_segs
        hx = heel_radius * 0.65 * math.cos(theta)
        hy = 115.5 + heel_radius * 0.45 * math.sin(theta)
        hz = -heel_depth
        verts.append((hx, hy, hz))
        
    for s in range(radial_segs):
        next_s = (s + 1) % radial_segs
        f1 = heel_start_idx + s
        f2 = heel_start_idx + next_s
        f3 = heel_rim_idx + next_s
        f4 = heel_rim_idx + s
        faces.append((f1, f2, f3, f4))
        
    flat_center_idx = len(verts)
    verts.append((0.0, 115.5, -heel_depth))
    for s in range(radial_segs):
        next_s = (s + 1) % radial_segs
        faces.append((flat_center_idx, heel_rim_idx + next_s, heel_rim_idx + s))
        
    return create_mesh_object("Gooseneck_Gankubi", verts, faces, mat_silver)


def build_bowl(mat_silver, mat_inner):
    """
    Constructs the small traditional upright bowl (gankubi-hizara) with:
    - Flared outward rim
    - Open upper cavity
    - Spherical bottom reservoir
    - Burnished / fire-tempered metal inner chamber
    """
    radial_segs = 32
    
    # Outer profile from base junction (z=14.5) up to rim (z=25.0)
    # Profile: (r, z)
    outer_profile = [
        (2.60, 14.5),
        (3.10, 15.5),
        (4.20, 17.5),
        (5.20, 20.0),
        (5.75, 22.8),
        (5.95, 24.6),
        (5.85, 25.2),  # Rounded lip edge
    ]
    
    # Inner cavity profile descending from rim down to bottom cavity
    inner_profile = [
        (5.40, 25.2),  # Top aperture opening
        (5.05, 24.2),
        (4.40, 22.0),
        (3.60, 19.5),
        (2.70, 17.5),
        (1.50, 16.2),
        (0.00, 15.8),  # Cavity center floor
    ]
    
    verts = []
    
    # Outer surface
    for r, z in outer_profile:
        for s in range(radial_segs):
            theta = 2.0 * math.pi * s / radial_segs
            x = r * math.cos(theta)
            y = 122.2 + r * math.sin(theta)
            verts.append((x, y, z))
            
    # Inner cavity surface
    inner_start_idx = len(verts)
    for idx, (r, z) in enumerate(inner_profile):
        if r == 0.0:
            verts.append((0.0, 122.2, z))
        else:
            for s in range(radial_segs):
                theta = 2.0 * math.pi * s / radial_segs
                x = r * math.cos(theta)
                y = 122.2 + r * math.sin(theta)
                verts.append((x, y, z))
                
    faces = []
    
    # Outer loft faces
    num_outer = len(outer_profile)
    for i in range(num_outer - 1):
        for s in range(radial_segs):
            next_s = (s + 1) % radial_segs
            v1 = i * radial_segs + s
            v2 = i * radial_segs + next_s
            v3 = (i + 1) * radial_segs + next_s
            v4 = (i + 1) * radial_segs + s
            faces.append((v1, v2, v3, v4))
            
    # Lip connecting ring: last outer ring to first inner ring
    lip_outer_start = (num_outer - 1) * radial_segs
    for s in range(radial_segs):
        next_s = (s + 1) % radial_segs
        o1 = lip_outer_start + s
        o2 = lip_outer_start + next_s
        i2 = inner_start_idx + next_s
        i1 = inner_start_idx + s
        faces.append((o1, o2, i2, i1))
        
    # Inner cavity loft faces
    num_inner = len(inner_profile)
    for i in range(num_inner - 2):
        r_curr = inner_start_idx + i * radial_segs
        r_next = inner_start_idx + (i + 1) * radial_segs
        for s in range(radial_segs):
            next_s = (s + 1) % radial_segs
            v1 = r_curr + s
            v2 = r_curr + next_s
            v3 = r_next + next_s
            v4 = r_next + s
            faces.append((v1, v4, v3, v2))
            
    # Fan faces to the bottom center apex
    center_idx = len(verts) - 1
    penultimate_start = inner_start_idx + (num_inner - 2) * radial_segs
    for s in range(radial_segs):
        next_s = (s + 1) % radial_segs
        p1 = penultimate_start + s
        p2 = penultimate_start + next_s
        faces.append((p1, p2, center_idx))
        
    bowl_obj = create_mesh_object("Bowl_Hizara", verts, faces, mat_silver)
    
    # Assign inner material to cavity polygons
    if mat_inner and len(bowl_obj.data.materials) < 2:
        bowl_obj.data.materials.append(mat_inner)
        cavity_face_threshold = (num_outer - 1) * radial_segs + radial_segs
        for f_idx in range(cavity_face_threshold, len(bowl_obj.data.polygons)):
            bowl_obj.data.polygons[f_idx].material_index = 1
            
    return bowl_obj


def build_reed_cord_wrap(mat_cord):
    """
    Constructs an authentic decorative bound rattan/reed cord wrap (saoto-maki)
    often found around traditional theatre and travel kiseru for grip and protection.
    Placed near the center node of the bamboo stem.
    """
    turns = 16
    segments_per_turn = 24
    total_segments = turns * segments_per_turn
    cord_radius = 0.55
    stem_r = 3.8
    y_start = -6.0
    y_length = 12.0
    
    verts = []
    faces = []
    cross_segs = 8
    
    centers = []
    tangents = []
    for step in range(total_segments + 1):
        t = step / total_segments
        angle = t * turns * 2.0 * math.pi
        y = y_start + t * y_length
        x = (stem_r + cord_radius * 0.6) * math.cos(angle)
        z = (stem_r + cord_radius * 0.6) * math.sin(angle)
        centers.append(Vector((x, y, z)))
        
    for idx in range(total_segments + 1):
        c = centers[idx]
        if idx < total_segments:
            tvec = (centers[idx + 1] - c).normalized()
        else:
            tvec = (c - centers[idx - 1]).normalized()
            
        up = Vector((0.0, 1.0, 0.0))
        side = tvec.cross(up).normalized()
        up = side.cross(tvec).normalized()
        
        for cs in range(cross_segs):
            theta = 2.0 * math.pi * cs / cross_segs
            offset = side * (math.cos(theta) * cord_radius) + up * (math.sin(theta) * cord_radius)
            pt = c + offset
            verts.append((pt.x, pt.y, pt.z))
            
    for i in range(total_segments):
        for cs in range(cross_segs):
            next_cs = (cs + 1) % cross_segs
            v1 = i * cross_segs + cs
            v2 = i * cross_segs + next_cs
            v3 = (i + 1) * cross_segs + next_cs
            v4 = (i + 1) * cross_segs + cs
            faces.append((v1, v2, v3, v4))
            
    return create_mesh_object("RattanGripWrap_Maki", verts, faces, mat_cord)


def build_model():
    """
    Main entry point for building the Traditional Japanese Kiseru Tobacco Pipe model.
    Compatible with Blender 5.2.2 standard API.
    """
    # 1. Prepare Materials
    # Aged golden bamboo with subtle satin gloss
    mat_bamboo = create_material(
        name="Kiseru_Bamboo",
        base_color=(0.68, 0.49, 0.24, 1.0),
        metallic=0.0,
        roughness=0.38,
        clearcoat=0.25
    )
    
    # Hand-polished Japanese silver alloy (shibuichi / silver-plated brass)
    mat_silver = create_material(
        name="Kiseru_PolishedSilver",
        base_color=(0.86, 0.88, 0.90, 1.0),
        metallic=0.92,
        roughness=0.18
    )
    
    # Antique brass for engraved connection ferrules and trims
    mat_brass = create_material(
        name="Kiseru_EngravedBrass",
        base_color=(0.82, 0.65, 0.28, 1.0),
        metallic=0.88,
        roughness=0.28
    )
    
    # Smoked interior bowl cavity (dark soot and patina)
    mat_interior = create_material(
        name="Kiseru_BowlCavity_Patina",
        base_color=(0.12, 0.11, 0.10, 1.0),
        metallic=0.45,
        roughness=0.75
    )
    
    # Dyed natural cane / rattan cord wrap
    mat_cord = create_material(
        name="Kiseru_RattanCord",
        base_color=(0.42, 0.28, 0.16, 1.0),
        metallic=0.0,
        roughness=0.65
    )

    # 2. Build Components
    parts = []
    
    # Slender central bamboo stem
    stem = build_bamboo_stem(mat_bamboo)
    parts.append(stem)
    
    # Front engraved ferrule (stem to gooseneck)
    ferrule_front = build_fitting_ferrule(
        name="Ferrule_GankubiJoint",
        y_offset=70.0,
        direction=1.0,
        mat_brass=mat_brass
    )
    parts.append(ferrule_front)
    
    # Rear engraved ferrule (stem to mouthpiece)
    ferrule_rear = build_fitting_ferrule(
        name="Ferrule_SuikuchiJoint",
        y_offset=-70.0,
        direction=-1.0,
        mat_brass=mat_brass
    )
    parts.append(ferrule_rear)
    
    # Mouthpiece
    mouthpiece = build_mouthpiece(mat_silver)
    parts.append(mouthpiece)
    
    # Gooseneck with heel
    gooseneck = build_gooseneck_and_heel(mat_silver)
    parts.append(gooseneck)
    
    # Bowl with cavity
    bowl = build_bowl(mat_silver, mat_interior)
    parts.append(bowl)
    
    # Traditional rattan grip binding
    cord_wrap = build_reed_cord_wrap(mat_cord)
    parts.append(cord_wrap)
    
    # 3. Create Root Hierarchy Empty near World Origin
    root_empty = bpy.data.objects.new("Japanese_Kiseru_Pipe", None)
    root_empty.empty_display_type = 'ARROWS'
    root_empty.empty_display_size = 20.0
    bpy.context.collection.objects.link(root_empty)
    
    # Center pipe gracefully across origin (offset so heel rests on ground Z=0)
    # The lowest point is heel z ~ -1.6, we place it so pipe rests stably
    elevation = 1.6
    root_empty.location = Vector((0.0, -10.0, elevation))
    
    for p in parts:
        p.parent = root_empty

    return root_empty


# Execute model creation if run directly as a script
if __name__ == "__main__":
    build_model()
