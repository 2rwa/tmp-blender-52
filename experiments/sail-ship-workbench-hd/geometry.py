"""Editable geometry primitives for an HD Workbench sailing ship."""
from __future__ import annotations
import math
import bpy
from mathutils import Vector

def material(name, rgb, metallic=0.0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1.0)
    m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=m.diffuse_color
    p.inputs["Metallic"].default_value=metallic
    p.inputs["Roughness"].default_value=0.63
    return m

def box(name,loc,size,mat,parent=None,bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    ob=bpy.context.object; ob.name=name; ob.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.data.materials.append(mat)
    if bevel:
        mod=ob.modifiers.new("Bevelled edges","BEVEL")
        mod.width=bevel; mod.segments=2
        ob.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
    if parent: ob.parent=parent
    return ob

def beam(name,a,b,width,mat,parent=None):
    d=Vector(b)-Vector(a)
    ob=box(name,(Vector(a)+Vector(b))/2,(width,width,d.length),mat,parent,0.008)
    ob.rotation_euler=d.to_track_quat("Z","Y").to_euler()
    return ob

def pole(name,loc,radius,length,mat,parent=None,rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=18,radius=radius,depth=length,
                                         location=loc,rotation=rotation)
    ob=bpy.context.object; ob.name=name; ob.data.materials.append(mat)
    ob.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
    if parent: ob.parent=parent
    return ob

def hull(parent,mat,trim):
    """Loft a curved wooden ship, bow toward X+; 10 stations, 8 points/section."""
    stations=[(-4.12,.38),(-3.75,.69),(-3.05,1.04),(-2.20,1.22),
              (-1.1,1.29),(0,1.31),(1.25,1.25),(2.4,1.04),
              (3.35,.65),(4.22,.055)]
    cross=[(1,2.08),(.98,1.71),(.83,.93),(.45,.24),
           (-.45,.24),(-.83,.93),(-.98,1.71),(-1,2.08)]
    vs=[]; fs=[]
    for x,halfbeam in stations:
        sheer=.12*(abs(x)/4.22)**2
        for y,z in cross:
            vs.append((x,y*halfbeam,z+sheer if z>.9 else z))
    for s in range(len(stations)-1):
        for j in range(7):
            a=s*8+j; b=(s+1)*8+j
            fs.append((a,a+1,b+1,b))
    fs.extend([tuple(range(7,-1,-1)),
               tuple((len(stations)-1)*8+j for j in range(8))])
    mesh=bpy.data.meshes.new("HullLoftMesh")
    mesh.from_pydata(vs,[],fs); mesh.update()
    ob=bpy.data.objects.new("Hull / section loft",mesh)
    bpy.context.collection.objects.link(ob)
    mesh.materials.append(mat); ob.parent=parent
    for face in mesh.polygons: face.use_smooth=True
    bev=ob.modifiers.new("Rounded bow and transom","BEVEL")
    bev.width=.055; bev.segments=2
    ob.modifiers.new("Smooth shading normals","WEIGHTED_NORMAL")
    for side in [-1,1]:
        for i in range(len(stations)-1):
            ax,aw=stations[i]; bx,bw=stations[i+1]
            beam("Gunwale %s-%d"%(side,i),
                 (ax,side*aw,2.10),(bx,side*bw,2.10),.055,trim,parent)
            beam("Hull strake %s-%d"%(side,i),
                 (ax,side*aw*.93,1.38),(bx,side*bw*.93,1.38),
                 .031,trim,parent)
    return ob

def sail(name,loc,width,height,mat,parent,fullness=.28,triangle=False):
    """Subdivided billowing square canvas; local XY -> world YZ."""
    cols,rows=19,14; vs=[]; fs=[]
    for j in range(rows):
        v=j/(rows-1)
        for i in range(cols):
            u=2*i/(cols-1)-1
            taper=(1-v*.91) if triangle else (1-v*.08)
            x=width*.5*taper*u
            y=height*(v-.5)
            z=fullness*(1-u*u)*math.sin(math.pi*(.07+.85*v))
            vs.append((x,y,z))
    for j in range(rows-1):
        for i in range(cols-1):
            a=j*cols+i
            fs.append((a,a+1,a+cols+1,a+cols))
    mesh=bpy.data.meshes.new(name+" Canvas Mesh")
    mesh.from_pydata(vs,[],fs); mesh.update()
    ob=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(ob)
    ob.location=loc
    ob.rotation_euler=(math.pi/2,0,math.pi/2)
    ob.data.materials.append(mat); ob.parent=parent
    for face in mesh.polygons: face.use_smooth=True
    thick=ob.modifiers.new("Cloth thickness","SOLIDIFY")
    thick.thickness=.019
    return ob

def ocean(water,foam):
    verts=[]; faces=[]; nx,ny=64,48
    for j in range(ny):
        y=-18+36*j/(ny-1)
        for i in range(nx):
            x=-20+40*i/(nx-1)
            z=.06*math.sin(x*.77+y*.28)+.07*math.sin(x*.29-y*.64)
            verts.append((x,y,z))
    for j in range(ny-1):
        for i in range(nx-1):
            a=j*nx+i
            faces.append((a,a+1,a+nx+1,a+nx))
    mesh=bpy.data.meshes.new("Ocean waves mesh")
    mesh.from_pydata(verts,[],faces); mesh.update()
    ob=bpy.data.objects.new("Blue Ocean",mesh)
    bpy.context.collection.objects.link(ob)
    mesh.materials.append(water)
    for face in mesh.polygons: face.use_smooth=True
    # Flat elliptical wake, not a vertical floating torus.
    bpy.ops.mesh.primitive_torus_add(major_radius=4.8,minor_radius=.075,
        major_segments=64,minor_segments=10,location=(-.25,0,.12))
    wake=bpy.context.object; wake.name="Wake / stylized foam"
    wake.scale=(1.0,.31,1.0)
    wake.data.materials.append(foam)
    return ob
