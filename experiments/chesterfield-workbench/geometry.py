"""Lightweight primitives for an editable Chesterfield Workbench scene."""
import math
import bpy
from mathutils import Vector


def material(name, rgb, metallic=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*rgb, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = .67
    return mat


def cuboid(name, pos, dims, mat, parent=None, bevel=.07):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Rounded upholstery edge', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    if parent:
        obj.parent = parent
    return obj


def cylinder(name, pos, radius, depth, mat, parent=None, rot=(0, 0, 0), vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
                                      depth=depth, location=pos, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    if parent:
        obj.parent = parent
    mod = obj.modifiers.new('Smooth end caps', 'BEVEL')
    mod.width = min(.035, radius * .25)
    mod.segments = 3
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj


def ball(name, pos, radii, mat, parent=None, segments=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=12,
                                          radius=1, location=pos)
    obj = bpy.context.object
    obj.name = name
    obj.scale = radii
    obj.data.materials.append(mat)
    for face in obj.data.polygons:
        face.use_smooth = True
    if parent:
        obj.parent = parent
    return obj


def tube(name, points, radius, mat, parent=None):
    curve = bpy.data.curves.new(name + ' curve', 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 12
    curve.bevel_depth = radius
    curve.resolution_u = 12
    curve.bevel_resolution = 2
    path = curve.splines.new('POLY')
    path.points.add(len(points) - 1)
    for bp, pt in zip(path.points, points):
        bp.co = (pt[0], pt[1], pt[2], 1)
    ob = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    if parent:
        ob.parent = parent
    return ob
