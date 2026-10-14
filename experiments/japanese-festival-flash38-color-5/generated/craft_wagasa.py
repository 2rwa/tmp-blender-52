"""
Japanese Wagasa Umbrella Generator for Blender 5.2.2.
Constructs an intricate traditional Japanese umbrella with canopy, bamboo ribs,
inner radial stretchers/spokes, decorative thread bindings, carved wooden shaft,
reinforced ferrule cap, and sliding runner.
"""

import bpy
import math
from mathutils import Vector, Matrix


def create_material(name, color_rgba, roughness=0.4, metallic=0.0):
    """
    Creates or retrieves a material, explicitly setting both:
    1) mat.diffuse_color for Workbench rendering (shading.color_type='MATERIAL').
    2) Principled BSDF 'Base Color' for EEVEE/Cycles rendering.
    """
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True

    # Critical for Workbench viewport/render
    mat.diffuse_color = color_rgba

    # Configure Principled BSDF node
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color_rgba
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic

    return mat


def link_mesh_object(name, mesh_data, parent_obj=None):
    """Links mesh data to the current scene collection, optionally setting parent."""
    obj = bpy.data.objects.new(name, mesh_data)
    bpy.context.collection.objects.link(obj)
    if parent_obj:
        obj.parent = parent_obj
    return obj


def create_canopy_mesh(num_ribs, rings, materials_dict):
    """
    Builds the faceted Japanese paper (washi) canopy with slight sagging between ribs.
    Assigns alternating Crimson (main), Gold accent band, and Cream inner border.
    """
    verts = []
    faces = []
    mat_indices = []

    # Apex vertex at center top
    apex_z = 1.30
    verts.append((0.0, 0.0, apex_z))

    # Rings from near-apex down to rim
    # Profile coordinates: (radius, z)
    profile = [
        (0.04, 1.28),
        (0.15, 1.25),
        (0.30, 1.18),
        (0.50, 1.05),
        (0.70, 0.88),
        (0.88, 0.70),
        (1.05, 0.50),
        (1.18, 0.35)
    ]

    num_rings = len(profile)

    for r_idx, (base_r, base_z) in enumerate(profile):
        for rib_idx in range(num_ribs):
            angle = (2.0 * math.pi * rib_idx) / num_ribs
            # Sag effect between ribs
            # We sample at the rib positions
            x = base_r * math.cos(angle)
            y = base_r * math.sin(angle)
            verts.append((x, y, base_z))

    # Generate faces for the top cone (apex to first ring)
    for i in range(num_ribs):
        next_i = (i + 1) % num_ribs
        v0 = 0
        v1 = 1 + i
        v2 = 1 + next_i
        faces.append((v0, v1, v2))
        mat_indices.append(0)  # Crimson

    # Generate quads between consecutive rings
    for r_idx in range(num_rings - 1):
        r_start = 1 + r_idx * num_ribs
        next_r_start = 1 + (r_idx + 1) * num_ribs

        # Determine band pattern for traditional look
        # r_idx == 3 or 4: Gold accent ring; outer ring: Cream border; else Crimson
        if r_idx in (3, 4):
            mat_idx = 1  # Gold
        elif r_idx == num_rings - 2:
            mat_idx = 2  # Cream
        else:
            mat_idx = 0  # Crimson

        for i in range(num_ribs):
            next_i = (i + 1) % num_ribs
            v0 = r_start + i
            v1 = r_start + next_i
            v2 = next_r_start + next_i
            v3 = next_r_start + i
            faces.append((v0, v1, v2, v3))
            mat_indices.append(mat_idx)

    mesh = bpy.data.meshes.new("WagasaCanopyMesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    # Assign materials
    mesh.materials.append(materials_dict["crimson"])  # 0
    mesh.materials.append(materials_dict["gold"])     # 1
    mesh.materials.append(materials_dict["cream"])    # 2

    for f_idx, mat_idx in enumerate(mat_indices):
        mesh.polygons[f_idx].material_index = mat_idx

    return mesh, profile


def create_cylinder_mesh(name, radius_top, radius_bot, height, segments=12, capped=True):
    """Constructs a clean cylindrical or conical mesh aligned along Z."""
    verts = []
    faces = []
    half_h = height * 0.5

    # Side vertices
    for i in range(segments):
        ang = (2.0 * math.pi * i) / segments
        c = math.cos(ang)
        s = math.sin(ang)
        verts.append((radius_bot * c, radius_bot * s, -half_h))
        verts.append((radius_top * c, radius_top * s, half_h))

    for i in range(segments):
        i_next = (i + 1) % segments
        b0 = i * 2
        t0 = i * 2 + 1
        b1 = i_next * 2
        t1 = i_next * 2 + 1
        faces.append((b0, b1, t1, t0))

    if capped:
        bot_center_idx = len(verts)
        verts.append((0.0, 0.0, -half_h))
        top_center_idx = len(verts)
        verts.append((0.0, 0.0, half_h))

        for i in range(segments):
            i_next = (i + 1) % segments
            b0 = i * 2
            b1 = i_next * 2
            t0 = i * 2 + 1
            t1 = i_next * 2 + 1
            faces.append((bot_center_idx, b1, b0))
            faces.append((top_center_idx, t0, t1))

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return mesh


def create_strut_mesh(name, length, width, thickness):
    """Creates a rectangular beam along the +X axis centered at origin."""
    hw = width * 0.5
    ht = thickness * 0.5
    verts = [
        (0.0, -hw, -ht), (length, -hw, -ht), (length, hw, -ht), (0.0, hw, -ht),
        (0.0, -hw,  ht), (length, -hw,  ht), (length, hw,  ht), (0.0, hw,  ht)
    ]
    faces = [
        (0, 1, 2, 3),  # Bottom
        (4, 7, 6, 5),  # Top
        (0, 4, 5, 1),  # Side -Y
        (2, 6, 7, 3),  # Side +Y
        (0, 3, 7, 4),  # End X=0
        (1, 5, 6, 2)   # End X=L
    ]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return mesh


def create_thread_web_mesh(num_ribs, inner_anchor_z, outer_anchor_pts, material):
    """
    Constructs the delicate decorative colored thread bindings (Kagarito)
    connecting the inner bamboo stretchers in geometric lattice loops.
    """
    verts = []
    edges = []

    # Two decorative lattice bands at fractional heights along the stretchers
    num_bands = 2
    for b_idx in range(num_bands):
        frac = 0.45 + b_idx * 0.25
        base_v = len(verts)
        for i in range(num_ribs):
            px, py, pz = outer_anchor_pts[i]
            x = px * frac
            y = py * frac
            z = inner_anchor_z + (pz - inner_anchor_z) * frac
            verts.append((x, y, z))

        for i in range(num_ribs):
            v0 = base_v + i
            v1 = base_v + ((i + 1) % num_ribs)
            v_cross = base_v + ((i + 2) % num_ribs)
            edges.append((v0, v1))
            edges.append((v0, v_cross))

    mesh = bpy.data.meshes.new("ThreadBindingsMesh")
    mesh.from_pydata(verts, edges, [])
    mesh.update()
    return mesh


def build_model():
    """
    Main entry point: Generates the full 3D model of a Japanese Wagasa umbrella.
    """
    # ----------------------------------------------------
    # 1. Palettes & Materials (diffuse_color matching BSDF)
    # ----------------------------------------------------
    materials = {
        # Vivid Japanese Vermilion/Crimson for Canopy
        "crimson": create_material("Wagasa_Crimson", (0.85, 0.08, 0.12, 1.0), roughness=0.55),
        # Polished Brass/Gold Accent Bands & Fittings
        "gold": create_material("Wagasa_Gold", (0.95, 0.76, 0.18, 1.0), roughness=0.30, metallic=0.7),
        # Natural Hand-made Cream Washi Paper
        "cream": create_material("Wagasa_WashiCream", (0.96, 0.92, 0.82, 1.0), roughness=0.65),
        # Split Bamboo Ribs & Spokes
        "bamboo": create_material("Wagasa_Bamboo", (0.78, 0.65, 0.42, 1.0), roughness=0.45),
        # Polished Dark Lacquered Wood Handle & Shaft
        "dark_wood": create_material("Wagasa_DarkWood", (0.16, 0.08, 0.05, 1.0), roughness=0.35),
        # Decorative Inner Binding Threads (Bright Silk)
        "silk_thread": create_material("Wagasa_SilkThread", (0.92, 0.22, 0.35, 1.0), roughness=0.5)
    }

    # Root empty container
    root = bpy.data.objects.new("Japanese_Wagasa", None)
    bpy.context.collection.objects.link(root)

    num_ribs = 36

    # ----------------------------------------------------
    # 2. Main Paper Canopy
    # ----------------------------------------------------
    canopy_mesh, profile = create_canopy_mesh(num_ribs, len(profile_data := [1]), materials)
    canopy_obj = link_mesh_object("Wagasa_Canopy", canopy_mesh, parent_obj=root)

    # ----------------------------------------------------
    # 3. Central Shaft & Carved Wooden Handle
    # ----------------------------------------------------
    # Main central bamboo/wood pole
    pole_mesh = create_cylinder_mesh("ShaftMesh", radius_top=0.014, radius_bot=0.014, height=1.55, segments=16)
    pole_obj = link_mesh_object("Wagasa_Shaft", pole_mesh, parent_obj=root)
    pole_obj.location = (0.0, 0.0, 0.60)
    pole_mesh.materials.append(materials["dark_wood"])

    # Carved lower handle grip with tapered end
    grip_mesh = create_cylinder_mesh("HandleMesh", radius_top=0.019, radius_bot=0.016, height=0.32, segments=16)
    grip_obj = link_mesh_object("Wagasa_HandleGrip", grip_mesh, parent_obj=root)
    grip_obj.location = (0.0, 0.0, -0.06)
    grip_mesh.materials.append(materials["dark_wood"])

    # Handle brass pommel ring at base
    pommel_mesh = create_cylinder_mesh("PommelMesh", radius_top=0.017, radius_bot=0.015, height=0.03, segments=16)
    pommel_obj = link_mesh_object("Wagasa_HandlePommel", pommel_mesh, parent_obj=root)
    pommel_obj.location = (0.0, 0.0, -0.235)
    pommel_mesh.materials.append(materials["gold"])

    # ----------------------------------------------------
    # 4. Top Hub (Atama-gami), Ferrule & Reinforced Cap
    # ----------------------------------------------------
    # Wooden apex cap housing the rib hinges
    hub_top_mesh = create_cylinder_mesh("HubTopMesh", radius_top=0.026, radius_bot=0.042, height=0.08, segments=24)
    hub_top_obj = link_mesh_object("Wagasa_ApexHub", hub_top_mesh, parent_obj=root)
    hub_top_obj.location = (0.0, 0.0, 1.28)
    hub_top_mesh.materials.append(materials["dark_wood"])

    # Reinforced tip finial (ferrule)
    finial_mesh = create_cylinder_mesh("FinialMesh", radius_top=0.008, radius_bot=0.018, height=0.10, segments=16)
    finial_obj = link_mesh_object("Wagasa_TipFinial", finial_mesh, parent_obj=root)
    finial_obj.location = (0.0, 0.0, 1.41)
    finial_mesh.materials.append(materials["dark_wood"])

    # Brass decorative collar at finial base
    finial_ring_mesh = create_cylinder_mesh("FinialRingMesh", radius_top=0.020, radius_bot=0.022, height=0.025, segments=16)
    finial_ring_obj = link_mesh_object("Wagasa_TipCollar", finial_ring_mesh, parent_obj=root)
    finial_ring_obj.location = (0.0, 0.0, 1.35)
    finial_ring_mesh.materials.append(materials["gold"])

    # ----------------------------------------------------
    # 5. Sliding Runner (Rokuro) along Shaft
    # ----------------------------------------------------
    runner_z = 0.65
    runner_mesh = create_cylinder_mesh("RunnerMesh", radius_top=0.036, radius_bot=0.028, height=0.07, segments=24)
    runner_obj = link_mesh_object("Wagasa_RunnerRokuro", runner_mesh, parent_obj=root)
    runner_obj.location = (0.0, 0.0, runner_z)
    runner_mesh.materials.append(materials["dark_wood"])

    # Brass ring on runner
    runner_ring_mesh = create_cylinder_mesh("RunnerRingMesh", radius_top=0.037, radius_bot=0.037, height=0.015, segments=20)
    runner_ring_obj = link_mesh_object("Wagasa_RunnerRing", runner_ring_mesh, parent_obj=root)
    runner_ring_obj.location = (0.0, 0.0, runner_z)
    runner_ring_mesh.materials.append(materials["gold"])

    # ----------------------------------------------------
    # 6. Bamboo Ribs (Canopy Support) & Inner Spokes
    # ----------------------------------------------------
    # Outer tip coordinates from the canopy profile
    outer_r, outer_z = profile[-1]
    top_r, top_z = profile[0]

    # Pre-calculate anchor positions for radial spokes
    spoke_outer_pts = []
    rib_length = math.sqrt((outer_r - top_r)**2 + (outer_z - top_z)**2)
    rib_angle_pitch = math.atan2(top_z - outer_z, outer_r - top_r)

    # Shared meshes for bamboo components for high polygon efficiency
    rib_mesh = create_strut_mesh("RibMesh", length=rib_length, width=0.009, thickness=0.005)
    rib_mesh.materials.append(materials["bamboo"])

    # Spoke dimensions
    # Connect from runner (radius ~0.03, runner_z) to middle of the rib
    mid_frac = 0.52
    mid_r = top_r + (outer_r - top_r) * mid_frac
    mid_z = top_z + (outer_z - top_z) * mid_frac
    spoke_dx = mid_r - 0.032
    spoke_dz = mid_z - runner_z
    spoke_length = math.sqrt(spoke_dx**2 + spoke_dz**2)
    spoke_pitch = math.atan2(spoke_dz, spoke_dx)

    spoke_mesh = create_strut_mesh("SpokeMesh", length=spoke_length, width=0.007, thickness=0.005)
    spoke_mesh.materials.append(materials["bamboo"])

    for i in range(num_ribs):
        yaw = (2.0 * math.pi * i) / num_ribs
        cos_y = math.cos(yaw)
        sin_y = math.sin(yaw)

        # 1) Long Canopy Rib
        rib_obj = bpy.data.objects.new(f"Wagasa_Rib_{i:02d}", rib_mesh)
        bpy.context.collection.objects.link(rib_obj)
        rib_obj.parent = root

        rib_obj.location = (top_r * cos_y, top_r * sin_y, top_z)
        rib_obj.rotation_mode = 'ZYX'
        rib_obj.rotation_euler = (0.0, rib_angle_pitch, yaw)

        # 2) Inner Spoke/Stretcher
        spoke_obj = bpy.data.objects.new(f"Wagasa_Spoke_{i:02d}", spoke_mesh)
        bpy.context.collection.objects.link(spoke_obj)
        spoke_obj.parent = root

        spoke_obj.location = (0.032 * cos_y, 0.032 * sin_y, runner_z)
        spoke_obj.rotation_mode = 'ZYX'
        spoke_obj.rotation_euler = (0.0, -spoke_pitch, yaw)

        # Record outer joint for thread web
        spoke_outer_pts.append((mid_r * cos_y, mid_r * sin_y, mid_z))

    # ----------------------------------------------------
    # 7. Decorative Silk Thread Bindings (Kagarito)
    # ----------------------------------------------------
    thread_mesh = create_thread_web_mesh(num_ribs, runner_z + 0.015, spoke_outer_pts, materials["silk_thread"])
    thread_obj = link_mesh_object("Wagasa_ThreadBindings", thread_mesh, parent_obj=root)
    thread_mesh.materials.append(materials["silk_thread"])

    # Add a thin bevel / solid geometry to thread mesh edges for tangible visibility
    wire_skin = thread_obj.modifiers.new(name="ThreadSkin", type='SOLIDIFY')
    wire_skin.thickness = 0.002
    wire_skin.offset = 0.0

    return root
