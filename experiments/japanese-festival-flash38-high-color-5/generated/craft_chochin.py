"""
Procedural Japanese Chochin Lantern Generator for Blender 5.2.
Constructs a traditional festival lantern featuring warm translucent paper,
ribbed bamboo armature, black lacquer framing, saturated red geometric
ornaments, upper bail and suspension ring, and an ornamental bottom tassel.
"""

import bpy
import math
import mathutils


def create_material(name, rgba, roughness=0.3, metallic=0.0):
    """
    Creates a material ensuring strict synchronization between Workbench diffuse_color
    and Principled BSDF Base Color.
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.diffuse_color = rgba
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = rgba
    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = roughness
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = metallic
    return mat


def create_mesh_object(name, verts, faces, material=None, parent=None, shade_smooth=True):
    """
    Instantiates an editable mesh object from vertices and faces,
    sets optional smooth shading, links material and assigns parent.
    """
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    if shade_smooth:
        for poly in mesh.polygons:
            poly.use_smooth = True
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    if material is not None:
        obj.data.materials.append(material)
    if parent is not None:
        obj.parent = parent
    bpy.context.scene.collection.objects.link(obj)
    return obj


def build_lathe_mesh(name, profile_pts, num_azimuth=48, material=None, parent=None, closed_v=False, shade_smooth=True):
    """
    Generates a surface of revolution around the Z axis from 2D profile coordinates (r, z).
    """
    verts = []
    faces = []
    num_v = len(profile_pts)
    for r, z in profile_pts:
        for j in range(num_azimuth):
            theta = 2.0 * math.pi * j / num_azimuth
            verts.append((r * math.cos(theta), r * math.sin(theta), z))

    v_limit = num_v if closed_v else num_v - 1
    for i in range(v_limit):
        next_i = (i + 1) % num_v
        for j in range(num_azimuth):
            next_j = (j + 1) % num_azimuth
            v0 = i * num_azimuth + j
            v1 = i * num_azimuth + next_j
            v2 = next_i * num_azimuth + next_j
            v3 = next_i * num_azimuth + j
            faces.append((v0, v1, v2, v3))

    return create_mesh_object(
        name=name,
        verts=verts,
        faces=faces,
        material=material,
        parent=parent,
        shade_smooth=shade_smooth,
    )


def build_tube_along_path(name, path_pts, radius=0.005, num_radial=12, material=None, parent=None, closed_path=False):
    """
    Sweeps a circular cross-section along a 3D path using rotation-minimizing transport frames.
    """
    num_pts = len(path_pts)
    if num_pts < 2:
        return None

    tangents = []
    for i in range(num_pts):
        if i == 0:
            t = mathutils.Vector(path_pts[1]) - mathutils.Vector(path_pts[0])
        elif i == num_pts - 1:
            t = mathutils.Vector(path_pts[-1]) - mathutils.Vector(path_pts[-2])
        else:
            t = mathutils.Vector(path_pts[i + 1]) - mathutils.Vector(path_pts[i - 1])
        if t.length < 1e-6:
            t = mathutils.Vector((0.0, 0.0, 1.0))
        else:
            t.normalize()
        tangents.append(t)

    frames = []
    t0 = tangents[0]
    up = mathutils.Vector((0.0, 0.0, 1.0))
    if abs(t0.dot(up)) > 0.9:
        up = mathutils.Vector((0.0, 1.0, 0.0))
    n0 = t0.cross(up).normalized()
    b0 = t0.cross(n0).normalized()
    frames.append((n0, b0))

    for i in range(1, num_pts):
        prev_t = tangents[i - 1]
        cur_t = tangents[i]
        prev_n, prev_b = frames[-1]
        axis = prev_t.cross(cur_t)
        if axis.length > 1e-6:
            angle = math.atan2(axis.length, prev_t.dot(cur_t))
            axis.normalize()
            rot = mathutils.Matrix.Rotation(angle, 3, axis)
            cur_n = (rot @ prev_n).normalized()
            cur_b = cur_t.cross(cur_n).normalized()
        else:
            cur_n = prev_n
            cur_b = prev_b
        frames.append((cur_n, cur_b))

    verts = []
    faces = []
    for i in range(num_pts):
        p = mathutils.Vector(path_pts[i])
        n, b = frames[i]
        for j in range(num_radial):
            theta = 2.0 * math.pi * j / num_radial
            v = p + radius * (math.cos(theta) * n + math.sin(theta) * b)
            verts.append((v.x, v.y, v.z))

    limit = num_pts if closed_path else num_pts - 1
    for i in range(limit):
        next_i = (i + 1) % num_pts
        for j in range(num_radial):
            next_j = (j + 1) % num_radial
            v0 = i * num_radial + j
            v1 = i * num_radial + next_j
            v2 = next_i * num_radial + next_j
            v3 = next_i * num_radial + j
            faces.append((v0, v1, v2, v3))

    if not closed_path:
        bottom_cap = [j for j in range(num_radial - 1, -1, -1)]
        top_offset = (num_pts - 1) * num_radial
        top_cap = [top_offset + j for j in range(num_radial)]
        faces.append(bottom_cap)
        faces.append(top_cap)

    return create_mesh_object(
        name=name,
        verts=verts,
        faces=faces,
        material=material,
        parent=parent,
        shade_smooth=True,
    )


def build_box(name, center, size, material=None, parent=None):
    """
    Constructs an axis-aligned box with explicit quad faces.
    """
    cx, cy, cz = center
    sx, sy, sz = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    verts = [
        (cx - sx, cy - sy, cz - sz),
        (cx + sx, cy - sy, cz - sz),
        (cx + sx, cy + sy, cz - sz),
        (cx - sx, cy + sy, cz - sz),
        (cx - sx, cy - sy, cz + sz),
        (cx + sx, cy - sy, cz + sz),
        (cx + sx, cy + sy, cz + sz),
        (cx - sx, cy + sy, cz + sz),
    ]
    faces = [
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (3, 7, 4, 0),
    ]
    return create_mesh_object(
        name=name,
        verts=verts,
        faces=faces,
        material=material,
        parent=parent,
        shade_smooth=False,
    )


def build_cylinder(name, base_z, top_z, radius, num_radial=24, material=None, parent=None):
    """
    Constructs a solid cylinder centered on the Z axis with flat end caps.
    """
    verts = []
    faces = []
    for j in range(num_radial):
        theta = 2.0 * math.pi * j / num_radial
        verts.append((radius * math.cos(theta), radius * math.sin(theta), base_z))
    for j in range(num_radial):
        theta = 2.0 * math.pi * j / num_radial
        verts.append((radius * math.cos(theta), radius * math.sin(theta), top_z))

    for j in range(num_radial):
        nj = (j + 1) % num_radial
        faces.append((j, nj, num_radial + nj, num_radial + j))

    bottom_cap = [j for j in range(num_radial - 1, -1, -1)]
    top_cap = [num_radial + j for j in range(num_radial)]
    faces.append(bottom_cap)
    faces.append(top_cap)

    return create_mesh_object(
        name=name,
        verts=verts,
        faces=faces,
        material=material,
        parent=parent,
        shade_smooth=True,
    )


def build_ring_torus(name, center, major_radius, minor_radius, num_major=36, num_minor=12, plane='XY', material=None, parent=None):
    """
    Constructs a toroidal ring in the specified coordinate plane.
    """
    verts = []
    faces = []
    cx, cy, cz = center
    for i in range(num_major):
        theta = 2.0 * math.pi * i / num_major
        for j in range(num_minor):
            phi = 2.0 * math.pi * j / num_minor
            r_cross = major_radius + minor_radius * math.cos(phi)
            z_cross = minor_radius * math.sin(phi)
            if plane == 'XY':
                x = cx + r_cross * math.cos(theta)
                y = cy + r_cross * math.sin(theta)
                z = cz + z_cross
            elif plane == 'YZ':
                x = cx + z_cross
                y = cy + r_cross * math.cos(theta)
                z = cz + r_cross * math.sin(theta)
            elif plane == 'XZ':
                x = cx + r_cross * math.cos(theta)
                y = cy + z_cross
                z = cz + r_cross * math.sin(theta)
            verts.append((x, y, z))

    for i in range(num_major):
        ni = (i + 1) % num_major
        for j in range(num_minor):
            nj = (j + 1) % num_minor
            v0 = i * num_minor + j
            v1 = i * num_minor + nj
            v2 = ni * num_minor + nj
            v3 = ni * num_minor + j
            faces.append((v0, v1, v2, v3))

    return create_mesh_object(
        name=name,
        verts=verts,
        faces=faces,
        material=material,
        parent=parent,
        shade_smooth=True,
    )


def lantern_surface_radius(z):
    """
    Calculates the outer radial envelope and bamboo rib wave of the paper body at height z.
    """
    t = (z + 0.35) / 0.70
    t_clamped = max(0.0, min(1.0, t))
    sin_val = math.sin(math.pi * t_clamped)
    r_env = 0.145 + (0.272 - 0.145) * (sin_val ** 0.75)
    r_rib = 0.0042 * math.cos(28.0 * math.pi * (2.0 * t_clamped - 1.0))
    return r_env + r_rib


def build_emblem(name, is_front, mat_red, mat_black, parent=None):
    """
    Constructs a traditional matsuri geometric heraldry badge (kamon) conforming
    to the lantern's barrel curvature. Includes outer ring, central sun disc,
    and stylized geometric lacquer bars with diamond crests.
    """
    sign_y = 1.0 if is_front else -1.0
    verts_red = []
    faces_red = []

    # 1. Outer Red Annular Ring
    r_out = 0.128
    r_in = 0.106
    n_ring = 36
    for j in range(n_ring):
        phi = 2.0 * math.pi * j / n_ring
        xo = r_out * math.cos(phi)
        zo = r_out * math.sin(phi)
        xi = r_in * math.cos(phi)
        zi = r_in * math.sin(phi)

        r_cyl_o = lantern_surface_radius(zo)
        yo = math.sqrt(max(0.001, r_cyl_o * r_cyl_o - xo * xo))
        r_cyl_i = lantern_surface_radius(zi)
        yi = math.sqrt(max(0.001, r_cyl_i * r_cyl_i - xi * xi))

        y_base_o = sign_y * (yo + 0.0022)
        y_front_o = y_base_o + sign_y * 0.003
        y_base_i = sign_y * (yi + 0.0022)
        y_front_i = y_base_i + sign_y * 0.003

        verts_red.append((xo, y_front_o, zo))
        verts_red.append((xi, y_front_i, zi))
        verts_red.append((xo, y_base_o, zo))
        verts_red.append((xi, y_base_i, zi))

    for j in range(n_ring):
        nj = (j + 1) % n_ring
        b = j * 4
        nb = nj * 4
        if is_front:
            faces_red.append((b + 0, nb + 0, nb + 1, b + 1))
            faces_red.append((b + 3, nb + 3, nb + 2, b + 2))
            faces_red.append((b + 0, b + 2, nb + 2, nb + 0))
            faces_red.append((b + 1, nb + 1, nb + 3, b + 3))
        else:
            faces_red.append((b + 0, b + 1, nb + 1, nb + 0))
            faces_red.append((b + 3, b + 2, nb + 2, nb + 3))
            faces_red.append((b + 0, nb + 0, nb + 2, b + 2))
            faces_red.append((b + 1, b + 3, nb + 3, nb + 1))

    # 2. Central Red Sun Disc
    r_disc = 0.086
    disc_offset = len(verts_red)
    r_cyl_c = lantern_surface_radius(0.0)
    yc = math.sqrt(max(0.001, r_cyl_c * r_cyl_c))
    verts_red.append((0.0, sign_y * (yc + 0.0052), 0.0))
    verts_red.append((0.0, sign_y * (yc + 0.0022), 0.0))

    for j in range(n_ring):
        phi = 2.0 * math.pi * j / n_ring
        xd = r_disc * math.cos(phi)
        zd = r_disc * math.sin(phi)
        r_cyl_d = lantern_surface_radius(zd)
        yd = math.sqrt(max(0.001, r_cyl_d * r_cyl_d - xd * xd))

        y_base_d = sign_y * (yd + 0.0022)
        y_front_d = y_base_d + sign_y * 0.003
        verts_red.append((xd, y_front_d, zd))
        verts_red.append((xd, y_base_d, zd))

    for j in range(n_ring):
        nj = (j + 1) % n_ring
        v_f = disc_offset + 2 + j * 2
        nv_f = disc_offset + 2 + nj * 2
        v_b = v_f + 1
        nv_b = nv_f + 1
        c_f = disc_offset + 0
        c_b = disc_offset + 1

        if is_front:
            faces_red.append((c_f, nv_f, v_f))
            faces_red.append((c_b, v_b, nv_b))
            faces_red.append((v_f, nv_f, nv_b, v_b))
        else:
            faces_red.append((c_f, v_f, nv_f))
            faces_red.append((c_b, nv_b, v_b))
            faces_red.append((v_f, v_b, nv_b, nv_f))

    create_mesh_object(
        name=f"{name}_Red",
        verts=verts_red,
        faces=faces_red,
        material=mat_red,
        parent=parent,
        shade_smooth=True,
    )

    # 3. Geometric Lacquer Black Bars & Diamond Badges
    verts_blk = []
    faces_blk = []

    bars = [
        (0.000, 0.124, 0.016),
        (0.034, 0.106, 0.014),
        (-0.034, 0.106, 0.014),
    ]

    for z_center, w_bar, h_bar in bars:
        hw = w_bar * 0.5
        hh = h_bar * 0.5
        box_pts = [
            (-hw, z_center - hh),
            (hw, z_center - hh),
            (hw, z_center + hh),
            (-hw, z_center + hh),
        ]
        b_idx = len(verts_blk)
        for bx, bz in box_pts:
            r_cyl_b = lantern_surface_radius(bz)
            yb = math.sqrt(max(0.001, r_cyl_b * r_cyl_b - bx * bx))
            y_base = sign_y * (yb + 0.0048)
            y_front = y_base + sign_y * 0.0028
            verts_blk.append((bx, y_front, bz))
            verts_blk.append((bx, y_base, bz))

        if is_front:
            faces_blk.append((b_idx + 0, b_idx + 2, b_idx + 4, b_idx + 6))
            faces_blk.append((b_idx + 7, b_idx + 5, b_idx + 3, b_idx + 1))
            for k in range(4):
                nk = (k + 1) % 4
                faces_blk.append((b_idx + k * 2, b_idx + nk * 2, b_idx + nk * 2 + 1, b_idx + k * 2 + 1))
        else:
            faces_blk.append((b_idx + 6, b_idx + 4, b_idx + 2, b_idx + 0))
            faces_blk.append((b_idx + 1, b_idx + 3, b_idx + 5, b_idx + 7))
            for k in range(4):
                nk = (k + 1) % 4
                faces_blk.append((b_idx + k * 2 + 1, b_idx + nk * 2 + 1, b_idx + nk * 2, b_idx + k * 2))

    # Diamond crests flanking the bars
    diamonds = [0.060, -0.060]
    for d_center in diamonds:
        d_sz = 0.013
        d_pts = [
            (0.0, d_center + d_sz),
            (d_sz, d_center),
            (0.0, d_center - d_sz),
            (-d_sz, d_center),
        ]
        d_idx = len(verts_blk)
        for dx, dz in d_pts:
            r_cyl_d = lantern_surface_radius(dz)
            yd = math.sqrt(max(0.001, r_cyl_d * r_cyl_d - dx * dx))
            y_base = sign_y * (yd + 0.0048)
            y_front = y_base + sign_y * 0.0028
            verts_blk.append((dx, y_front, dz))
            verts_blk.append((dx, y_base, dz))

        if is_front:
            faces_blk.append((d_idx + 0, d_idx + 2, d_idx + 4, d_idx + 6))
            faces_blk.append((d_idx + 7, d_idx + 5, d_idx + 3, d_idx + 1))
            for k in range(4):
                nk = (k + 1) % 4
                faces_blk.append((d_idx + k * 2, d_idx + nk * 2, d_idx + nk * 2 + 1, d_idx + k * 2 + 1))
        else:
            faces_blk.append((d_idx + 6, d_idx + 4, d_idx + 2, d_idx + 0))
            faces_blk.append((d_idx + 1, d_idx + 3, d_idx + 5, d_idx + 7))
            for k in range(4):
                nk = (k + 1) % 4
                faces_blk.append((d_idx + k * 2 + 1, d_idx + nk * 2 + 1, d_idx + nk * 2, d_idx + k * 2))

    create_mesh_object(
        name=f"{name}_Black",
        verts=verts_blk,
        faces=faces_blk,
        material=mat_black,
        parent=parent,
        shade_smooth=False,
    )


def build_model():
    """
    Constructs the complete 3D procedural Japanese Chochin Lantern model.
    """
    # -------------------------------------------------------------------------
    # 1. Workbench High-Contrast Materials
    # -------------------------------------------------------------------------
    mat_paper = create_material("Chochin_Paper_WarmWhite", (0.96, 0.93, 0.82, 1.0), roughness=0.85, metallic=0.0)
    mat_red = create_material("Chochin_Festival_Red", (0.86, 0.07, 0.05, 1.0), roughness=0.35, metallic=0.0)
    mat_lacquer = create_material("Chochin_Lacquer_Black", (0.04, 0.04, 0.05, 1.0), roughness=0.15, metallic=0.0)
    mat_brass = create_material("Chochin_Brass_Gold", (0.90, 0.72, 0.20, 1.0), roughness=0.25, metallic=0.9)
    mat_bamboo = create_material("Chochin_Bamboo_Dark", (0.22, 0.14, 0.08, 1.0), roughness=0.60, metallic=0.0)
    mat_silk_gold = create_material("Chochin_Silk_Gold", (0.96, 0.82, 0.28, 1.0), roughness=0.40, metallic=0.0)
    mat_iron = create_material("Chochin_Iron_Black", (0.12, 0.13, 0.14, 1.0), roughness=0.50, metallic=0.7)

    # -------------------------------------------------------------------------
    # 2. Main Root Object
    # -------------------------------------------------------------------------
    root = bpy.data.objects.new("Chochin_Lantern", None)
    bpy.context.scene.collection.objects.link(root)
    root.location = (0.0, 0.0, 0.0)

    # -------------------------------------------------------------------------
    # 3. Ribbed Paper Lantern Body (Double-Walled Solid Shell)
    # -------------------------------------------------------------------------
    v_steps = 140
    outer_pts = []
    inner_pts = []
    for i in range(v_steps + 1):
        t = i / v_steps
        z = -0.35 + 0.70 * t
        r_out = lantern_surface_radius(z)
        r_in = r_out - 0.0035
        outer_pts.append((r_out, z))
        inner_pts.append((r_in, z))

    # Create closed cross-section profile: outer wall up, lip, inner wall down, bottom lip
    paper_profile = []
    paper_profile.extend(outer_pts)
    paper_profile.extend(reversed(inner_pts))

    build_lathe_mesh(
        name="Chochin_Paper_Body",
        profile_pts=paper_profile,
        num_azimuth=64,
        material=mat_paper,
        parent=root,
        closed_v=True,
        shade_smooth=True,
    )

    # -------------------------------------------------------------------------
    # 4. Embedded Bamboo Rib Rings (Armature Hoops)
    # -------------------------------------------------------------------------
    rib_verts = []
    rib_faces = []
    num_rib_segments = 48
    # 25 bamboo hoops along the paper ridge crests
    for rib_idx in range(2, 27):
        t_rib = rib_idx / 28.0
        z_rib = -0.35 + 0.70 * t_rib
        r_ridge = lantern_surface_radius(z_rib)
        base_v = len(rib_verts)

        for j in range(num_rib_segments):
            phi = 2.0 * math.pi * j / num_rib_segments
            cos_p = math.cos(phi)
            sin_p = math.sin(phi)

            p_out = ((r_ridge + 0.0022) * cos_p, (r_ridge + 0.0022) * sin_p, z_rib)
            p_top = ((r_ridge + 0.0004) * cos_p, (r_ridge + 0.0004) * sin_p, z_rib + 0.0022)
            p_in = ((r_ridge - 0.0016) * cos_p, (r_ridge - 0.0016) * sin_p, z_rib)
            p_bot = ((r_ridge + 0.0004) * cos_p, (r_ridge + 0.0004) * sin_p, z_rib - 0.0022)

            rib_verts.extend([p_out, p_top, p_in, p_bot])

        for j in range(num_rib_segments):
            nj = (j + 1) % num_rib_segments
            v0 = base_v + j * 4
            v1 = base_v + nj * 4
            rib_faces.append((v0 + 0, v0 + 1, v1 + 1, v1 + 0))
            rib_faces.append((v0 + 1, v0 + 2, v1 + 2, v1 + 1))
            rib_faces.append((v0 + 2, v0 + 3, v1 + 3, v1 + 2))
            rib_faces.append((v0 + 3, v0 + 0, v1 + 0, v1 + 3))

    create_mesh_object(
        name="Chochin_Bamboo_Ribs",
        verts=rib_verts,
        faces=rib_faces,
        material=mat_bamboo,
        parent=root,
        shade_smooth=True,
    )

    # -------------------------------------------------------------------------
    # 5. Upper and Lower Saturated Red Festival Bands
    # -------------------------------------------------------------------------
    bands_data = [
        (0.225, 0.305, 12),
        (-0.305, -0.225, 12),
    ]
    band_verts = []
    band_faces = []
    for z_start, z_end, n_sub in bands_data:
        b_offset = len(band_verts)
        band_prof = []
        for s in range(n_sub + 1):
            bz = z_start + (z_end - z_start) * (s / n_sub)
            br_out = lantern_surface_radius(bz) + 0.0014
            br_in = br_out - 0.0009
            band_prof.append((br_out, br_in, bz))

        num_az = 48
        for ro, ri, bz in band_prof:
            for j in range(num_az):
                phi = 2.0 * math.pi * j / num_az
                band_verts.append((ro * math.cos(phi), ro * math.sin(phi), bz))
                band_verts.append((ri * math.cos(phi), ri * math.sin(phi), bz))

        for s in range(n_sub):
            for j in range(num_az):
                nj = (j + 1) % num_az
                row_cur = b_offset + s * (num_az * 2)
                row_next = b_offset + (s + 1) * (num_az * 2)

                # Outer quad
                band_faces.append((row_cur + j * 2, row_next + j * 2, row_next + nj * 2, row_cur + nj * 2))
                # Inner quad
                band_faces.append((row_cur + nj * 2 + 1, row_next + nj * 2 + 1, row_next + j * 2 + 1, row_cur + j * 2 + 1))

        # Bottom lip
        for j in range(num_az):
            nj = (j + 1) % num_az
            band_faces.append((b_offset + j * 2, b_offset + nj * 2, b_offset + nj * 2 + 1, b_offset + j * 2 + 1))

        # Top lip
        top_row = b_offset + n_sub * (num_az * 2)
        for j in range(num_az):
            nj = (j + 1) % num_az
            band_faces.append((top_row + nj * 2, top_row + j * 2, top_row + j * 2 + 1, top_row + nj * 2 + 1))

    create_mesh_object(
        name="Chochin_Bands_Red",
        verts=band_verts,
        faces=band_faces,
        material=mat_red,
        parent=root,
        shade_smooth=True,
    )

    # -------------------------------------------------------------------------
    # 6. Matsuri Geometric Crests (Front & Back)
    # -------------------------------------------------------------------------
    build_emblem(name="Chochin_Emblem_Front", is_front=True, mat_red=mat_red, mat_black=mat_lacquer, parent=root)
    build_emblem(name="Chochin_Emblem_Back", is_front=False, mat_red=mat_red, mat_black=mat_lacquer, parent=root)

    # -------------------------------------------------------------------------
    # 7. Upper Black Lacquer Wood Collar & Brass Trim
    # -------------------------------------------------------------------------
    top_collar_profile = [
        (0.150, 0.340),
        (0.160, 0.352),
        (0.168, 0.365),
        (0.174, 0.372),
        (0.168, 0.379),
        (0.168, 0.418),
        (0.164, 0.428),
        (0.156, 0.430),
        (0.144, 0.430),
        (0.138, 0.422),
        (0.138, 0.340),
    ]
    build_lathe_mesh(
        name="Chochin_Top_Collar",
        profile_pts=top_collar_profile,
        num_azimuth=48,
        material=mat_lacquer,
        parent=root,
        closed_v=True,
        shade_smooth=True,
    )

    top_brass_profile = [
        (0.1755, 0.368),
        (0.1755, 0.376),
        (0.1740, 0.376),
        (0.1740, 0.368),
    ]
    build_lathe_mesh(
        name="Chochin_Top_Brass_Trim",
        profile_pts=top_brass_profile,
        num_azimuth=48,
        material=mat_brass,
        parent=root,
        closed_v=True,
        shade_smooth=True,
    )

    # -------------------------------------------------------------------------
    # 8. Lower Black Lacquer Wood Collar & Brass Trim
    # -------------------------------------------------------------------------
    bottom_collar_profile = [
        (0.150, -0.340),
        (0.160, -0.352),
        (0.168, -0.365),
        (0.174, -0.372),
        (0.168, -0.379),
        (0.168, -0.418),
        (0.164, -0.428),
        (0.156, -0.430),
        (0.144, -0.430),
        (0.138, -0.422),
        (0.138, -0.340),
    ]
    build_lathe_mesh(
        name="Chochin_Bottom_Collar",
        profile_pts=bottom_collar_profile,
        num_azimuth=48,
        material=mat_lacquer,
        parent=root,
        closed_v=True,
        shade_smooth=True,
    )

    bottom_brass_profile = [
        (0.1755, -0.376),
        (0.1755, -0.368),
        (0.1740, -0.368),
        (0.1740, -0.376),
    ]
    build_lathe_mesh(
        name="Chochin_Bottom_Brass_Trim",
        profile_pts=bottom_brass_profile,
        num_azimuth=48,
        material=mat_brass,
        parent=root,
        closed_v=True,
        shade_smooth=True,
    )

    # Bottom Base Floor with Central Port
    bottom_floor_profile = [
        (0.024, -0.424),
        (0.140, -0.424),
        (0.140, -0.430),
        (0.024, -0.430),
    ]
    build_lathe_mesh(
        name="Chochin_Bottom_Floor",
        profile_pts=bottom_floor_profile,
        num_azimuth=36,
        material=mat_lacquer,
        parent=root,
        closed_v=True,
        shade_smooth=True,
    )

    # Bottom Brass Eyelet Fitting
    build_cylinder(
        name="Chochin_Bottom_Boss",
        base_z=-0.434,
        top_z=-0.424,
        radius=0.028,
        num_radial=24,
        material=mat_brass,
        parent=root,
    )
    build_ring_torus(
        name="Chochin_Bottom_Eyelet",
        center=(0.0, 0.0, -0.444),
        major_radius=0.012,
        minor_radius=0.0028,
        num_major=24,
        num_minor=10,
        plane='YZ',
        material=mat_brass,
        parent=root,
    )

    # -------------------------------------------------------------------------
    # 9. Top Crossbar, Side Mounting Brackets and Hardware
    # -------------------------------------------------------------------------
    build_box(
        name="Chochin_Top_Crossbar",
        center=(0.0, 0.0, 0.406),
        size=(0.288, 0.024, 0.018),
        material=mat_lacquer,
        parent=root,
    )
    build_cylinder(
        name="Chochin_Top_Center_Pin",
        base_z=0.406,
        top_z=0.426,
        radius=0.009,
        num_radial=16,
        material=mat_brass,
        parent=root,
    )

    # Side Brass Mounting Brackets (Kanezashi) with Pivot Bosses
    for sign_x in [-1.0, 1.0]:
        x_pos = sign_x * 0.170
        build_box(
            name=f"Chochin_Side_Bracket_{'R' if sign_x > 0 else 'L'}",
            center=(x_pos, 0.0, 0.392),
            size=(0.010, 0.022, 0.034),
            material=mat_brass,
            parent=root,
        )
        build_box(
            name=f"Chochin_Side_Boss_{'R' if sign_x > 0 else 'L'}",
            center=(x_pos + sign_x * 0.007, 0.0, 0.392),
            size=(0.008, 0.012, 0.012),
            material=mat_brass,
            parent=root,
        )

    # -------------------------------------------------------------------------
    # 10. Upper Suspension Bail (Handle) & Hanging Ring
    # -------------------------------------------------------------------------
    arch_pts = []
    num_arch = 36
    for i in range(num_arch):
        th = math.pi * i / (num_arch - 1)
        ax = 0.174 * math.cos(th)
        az = 0.392 + 0.218 * math.sin(th)
        arch_pts.append((ax, 0.0, az))

    build_tube_along_path(
        name="Chochin_Hanger_Bail",
        path_pts=arch_pts,
        radius=0.0055,
        num_radial=14,
        material=mat_iron,
        parent=root,
        closed_path=False,
    )

    # Apex Brass Cuff Ferrule
    cuff_pts = [
        (-0.018, 0.0, 0.610),
        (0.018, 0.0, 0.610),
    ]
    build_tube_along_path(
        name="Chochin_Apex_Cuff",
        path_pts=cuff_pts,
        radius=0.0085,
        num_radial=16,
        material=mat_brass,
        parent=root,
        closed_path=False,
    )

    # Upper Brass Suspension Ring
    build_ring_torus(
        name="Chochin_Suspension_Ring",
        center=(0.0, 0.0, 0.648),
        major_radius=0.034,
        minor_radius=0.0048,
        num_major=36,
        num_minor=12,
        plane='YZ',
        material=mat_brass,
        parent=root,
    )

    # -------------------------------------------------------------------------
    # 11. Ornamental Bottom Tassel (Fusa) Assembly
    # -------------------------------------------------------------------------
    # Suspension Cord
    cord_pts = [
        (0.0, 0.0, -0.445),
        (0.0, 0.0, -0.520),
    ]
    build_tube_along_path(
        name="Chochin_Tassel_Cord",
        path_pts=cord_pts,
        radius=0.0042,
        num_radial=12,
        material=mat_red,
        parent=root,
        closed_path=False,
    )

    # Traditional Agemaki Knot Center Block
    build_box(
        name="Chochin_Agemaki_Center",
        center=(0.0, 0.0, -0.526),
        size=(0.026, 0.016, 0.022),
        material=mat_red,
        parent=root,
    )

    # Agemaki Side Wing Loops
    for side_x in [-1.0, 1.0]:
        wing_pts = [
            (side_x * 0.011, 0.0, -0.524),
            (side_x * 0.024, 0.0, -0.514),
            (side_x * 0.038, 0.0, -0.518),
            (side_x * 0.044, 0.0, -0.530),
            (side_x * 0.034, 0.0, -0.542),
            (side_x * 0.020, 0.0, -0.538),
            (side_x * 0.011, 0.0, -0.530),
        ]
        build_tube_along_path(
            name=f"Chochin_Agemaki_Wing_{'R' if side_x > 0 else 'L'}",
            path_pts=wing_pts,
            radius=0.0032,
            num_radial=10,
            material=mat_red,
            parent=root,
            closed_path=False,
        )

    # Cord drops connecting knot to tassel cap
    for side_x in [-1.0, 1.0]:
        drop_pts = [
            (side_x * 0.005, 0.0, -0.532),
            (side_x * 0.004, 0.0, -0.554),
        ]
        build_tube_along_path(
            name=f"Chochin_Knot_Drop_{'R' if side_x > 0 else 'L'}",
            path_pts=drop_pts,
            radius=0.0034,
            num_radial=10,
            material=mat_red,
            parent=root,
            closed_path=False,
        )

    # Brass Tassel Cap / Ferrule (Fusa-gashira)
    tassel_cap_profile = [
        (0.008, -0.532),
        (0.011, -0.538),
        (0.014, -0.548),
        (0.019, -0.558),
        (0.024, -0.565),
        (0.020, -0.565),
        (0.006, -0.532),
    ]
    build_lathe_mesh(
        name="Chochin_Tassel_Cap",
        profile_pts=tassel_cap_profile,
        num_azimuth=32,
        material=mat_brass,
        parent=root,
        closed_v=True,
        shade_smooth=True,
    )

    # Gold Silk Thread Neck Binding
    neck_profile = [
        (0.0215, -0.565),
        (0.0215, -0.588),
        (0.0195, -0.588),
        (0.0195, -0.565),
    ]
    build_lathe_mesh(
        name="Chochin_Tassel_Gold_Band",
        profile_pts=neck_profile,
        num_azimuth=32,
        material=mat_silk_gold,
        parent=root,
        closed_v=True,
        shade_smooth=True,
    )

    # Two-Tiered Fluted Silk Tassel Skirt (Fringes)
    fringe_verts = []
    fringe_faces = []
    tiers = [
        (-0.586, -0.730, 0.021, 0.038, 16, 16, 0.06),  # Outer Tier
        (-0.586, -0.850, 0.017, 0.030, 20, 12, 0.05),  # Inner Core Tier
    ]

    for z_top, z_bot, r_top, r_bot, v_cnt, n_flutes, amp in tiers:
        t_offset = len(fringe_verts)
        num_az = 48
        for vi in range(v_cnt + 1):
            fv = vi / v_cnt
            fz = z_top + (z_bot - z_top) * fv
            base_r = r_top + (r_bot - r_top) * (fv ** 0.88)
            for j in range(num_az):
                phi = 2.0 * math.pi * j / num_az
                r_fluted = base_r * (1.0 + amp * math.cos(n_flutes * phi))
                fringe_verts.append((r_fluted * math.cos(phi), r_fluted * math.sin(phi), fz))

        for vi in range(v_cnt):
            for j in range(num_az):
                nj = (j + 1) % num_az
                v0 = t_offset + vi * num_az + j
                v1 = t_offset + vi * num_az + nj
                v2 = t_offset + (vi + 1) * num_az + nj
                v3 = t_offset + (vi + 1) * num_az + j
                fringe_faces.append((v0, v1, v2, v3))

        # Bottom rim closure
        bot_offset = t_offset + v_cnt * num_az
        fringe_faces.append([bot_offset + j for j in range(num_az - 1, -1, -1)])

    create_mesh_object(
        name="Chochin_Tassel_Fringe",
        verts=fringe_verts,
        faces=fringe_faces,
        material=mat_red,
        parent=root,
        shade_smooth=True,
    )

    # -------------------------------------------------------------------------
    # 12. Interior Candle Perch and Brass Spike (Rosoku-tate)
    # -------------------------------------------------------------------------
    build_cylinder(
        name="Chochin_Interior_Perch",
        base_z=-0.312,
        top_z=-0.300,
        radius=0.044,
        num_radial=24,
        material=mat_lacquer,
        parent=root,
    )

    spike_profile = [
        (0.0055, -0.300),
        (0.0035, -0.250),
        (0.0010, -0.220),
        (0.0000, -0.220),
        (0.0000, -0.300),
    ]
    build_lathe_mesh(
        name="Chochin_Interior_Spike",
        profile_pts=spike_profile,
        num_azimuth=16,
        material=mat_brass,
        parent=root,
        closed_v=True,
        shade_smooth=True,
    )
