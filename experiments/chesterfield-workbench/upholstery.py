"""Geometric leather tufting with depressed buttons and piped diamond seams."""
import math
import bpy
from mathutils import Vector
from geometry import ball, tube


def button_locations(width, height, cols, rows):
    locs = []
    for j in range(rows + 1):
        y = -height * .42 + j * height * .84 / rows
        shift = .5 if j % 2 else 0
        for i in range(cols + 1):
            x = -width * .42 + (i + shift) * width * .84 / cols
            if abs(x) <= width * .465:
                locs.append((x, y))
    return locs


def height_at(x, y, width, height, centers, relief):
    """Dense inflated leather surface with smooth depressions at each button."""
    sx = width / max(1, int(width / .24) + 1)
    sy = height / max(1, int(height / .25) + 1)
    d = min(((x - px) / sx)**2 + ((y - py) / sy)**2 for px, py in centers)
    pillowy = .065 * (1 - (x / (width * .57))**2) * (1 - (y / (height * .57))**2)
    return relief * (.20 - .92 * math.exp(-d / .30)) + pillowy


def tufted(name, width, height, cols, rows, pos, rot, leather, button_mat,
           seam_mat, parent, relief=.12):
    nx, ny = max(38, cols * 16 + 1), max(40, rows * 15 + 1)
    centers = button_locations(width, height, cols, rows)
    verts, faces = [], []
    for j in range(ny):
        y = height * (j / (ny - 1) - .5)
        for i in range(nx):
            x = width * (i / (nx - 1) - .5)
            z = height_at(x, y, width, height, centers, relief)
            verts.append((x, y, z))
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            faces.append((a, a + 1, a + nx + 1, a + nx))
    mesh = bpy.data.meshes.new(name + ' quilt mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(leather)
    for face in mesh.polygons:
        face.use_smooth = True
    solid = ob.modifiers.new('Padded leather backing', 'SOLIDIFY')
    solid.thickness = .12
    ob.location = pos
    ob.rotation_euler = rot
    ob.parent = parent
    for k, (x, y) in enumerate(centers):
        z = height_at(x, y, width, height, centers, relief) + .022
        ball('%s / inset button %02d' % (name, k), (x, y, z),
             (.031, .031, .013), button_mat, ob, 12)
    # Diamond welt: curved diagonal stitching between alternating button rows.
    seam_count = 0
    # Join nearby alternating-row fasteners, sampling the real leather surface.
    rowstep = height * .84 / rows
    colstep = width * .84 / cols
    for i, (x, y) in enumerate(centers):
        for xx, yy in centers[i + 1:]:
            if abs(yy - y - rowstep) > .0001 or abs(abs(xx - x) - colstep * .5) > .005:
                continue
            points = []
            for n in range(10):
                t = n / 9
                px, py = x * (1 - t) + xx * t, y * (1 - t) + yy * t
                points.append((px, py, height_at(px, py, width, height, centers, relief) + .004))
            tube('%s / diamond seam %02d' % (name, seam_count),
                 points, .0055, seam_mat, ob)
            seam_count += 1
    return ob, len(centers), seam_count
