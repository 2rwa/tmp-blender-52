import math
import bpy
from mathutils import Vector
PALETTE={"wood":(.49,.27,.13,1),"wood2":(.7,.45,.22,1),"bamboo":(.65,.64,.32,1),"bamboo2":(.43,.57,.30,1),"leaf":(.36,.49,.25,1),"paper":(.92,.84,.65,1),"white":(.93,.91,.83,1),"red":(.78,.16,.13,1),"vermilion":(.94,.31,.16,1),"blue":(.18,.39,.58,1),"indigo":(.13,.22,.38,1),"green":(.27,.48,.31,1),"gold":(.88,.67,.22,1),"iron":(.22,.26,.28,1),"black":(.12,.13,.15,1),"clay":(.71,.45,.32,1),"pink":(.89,.51,.52,1),"orange":(.91,.47,.16,1),"gray":(.53,.54,.5,1)}
M={}
def init():
 for k,v in PALETTE.items():
  m=bpy.data.materials.new(k);m.diffuse_color=v;M[k]=m
def bind(o,name,color):
 o.name=name;o.data.materials.append(M[color]);return o
def box(name,p,d,color):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bind(bpy.context.object,name,color)
 o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return o
def cyl(name,p,r,h,color,n=12,top=None):
 if top is None:bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=h,location=p)
 else:bpy.ops.mesh.primitive_cone_add(vertices=n,radius1=r,radius2=top,depth=h,location=p)
 return bind(bpy.context.object,name,color)
def orb(name,p,d,color,sub=1):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=p)
 o=bind(bpy.context.object,name,color);o.scale=d;return o
def rod(name,a,b,r,color,n=8):
 a=Vector(a);b=Vector(b);d=b-a
 if d.length<.00001:return None
 o=cyl(name,tuple((a+b)*.5),r,d.length,color,n)
 o.rotation_euler=d.to_track_quat("Z","Y").to_euler();return o
def ring(name,p,R,r,color,n=16,axis="Z"):
 bpy.ops.mesh.primitive_torus_add(major_segments=n,minor_segments=5,location=p,major_radius=R,minor_radius=r)
 o=bind(bpy.context.object,name,color)
 if axis=="X":o.rotation_euler[1]=math.pi/2
 if axis=="Y":o.rotation_euler[0]=math.pi/2
 return o
def bend(name,pts,color,r=.025):
 for i in range(len(pts)-1):rod(name+str(i),pts[i],pts[i+1],r,color,6)
