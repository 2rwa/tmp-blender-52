"""Geometry tools for recognizable, richly built Japanese objects.
Blender 5.2; all geometry is generated as real meshes and exported to GLB.
"""
import math
import bpy
from mathutils import Vector

PALETTE={
 "cedar":(.42,.23,.105,1),"hinoki":(.77,.56,.31,1),
 "wooddark":(.20,.12,.075,1),"bamboo":(.59,.62,.29,1),
 "bamboodark":(.26,.39,.17,1),"washi":(.96,.87,.68,1),
 "ivory":(.97,.92,.82,1),"red":(.78,.10,.095,1),
 "vermilion":(.96,.25,.11,1),"lacquer":(.15,.08,.09,1),
 "indigo":(.075,.20,.36,1),"blue":(.18,.42,.62,1),
 "celadon":(.42,.69,.58,1),"jade":(.11,.37,.31,1),
 "iron":(.20,.24,.26,1),"steel":(.57,.63,.65,1),
 "gold":(.87,.66,.22,1),"bronze":(.46,.32,.16,1),
 "clay":(.59,.34,.22,1),"cream":(.82,.70,.53,1),
 "pink":(.94,.55,.59,1),"orange":(.94,.44,.11,1),
 "black":(.06,.068,.080,1),"charcoal":(.22,.23,.25,1),
 "fabric":(.55,.19,.28,1),"straw":(.80,.66,.35,1),
 "green":(.22,.45,.23,1)
}
M={}
def init():
 M.clear()
 for name,col in PALETTE.items():
  mat=bpy.data.materials.get("CRAFT_"+name) or bpy.data.materials.new("CRAFT_"+name)
  mat.diffuse_color=col
  mat.use_nodes=True
  bs=mat.node_tree.nodes.get("Principled BSDF")
  if bs:bs.inputs["Base Color"].default_value=col
  M[name]=mat

def mesh(name,vertices,faces,color):
 me=bpy.data.meshes.new(name)
 me.from_pydata(vertices,[],faces);me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
 ob.data.materials.append(M[color])
 return ob

def bind(ob,name,color):
 ob.name=name
 ob.data.materials.append(M[color])
 return ob

def box(name,pos,dim,color,bevel=.018):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos)
 o=bind(bpy.context.object,name,color)
 o.dimensions=dim
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new("Rounded timber edges","BEVEL")
  mod.width=min(bevel,min(dim)*.30)
  mod.segments=2
  mod.affect="EDGES"
  bpy.context.view_layer.objects.active=o
  bpy.ops.object.modifier_apply(modifier=mod.name)
 return o

def cyl(name,pos,r,h,color,n=24,top=None):
 if top is None:
  bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=h,location=pos)
 else:
  bpy.ops.mesh.primitive_cone_add(vertices=n,radius1=r,radius2=top,depth=h,location=pos)
 return bind(bpy.context.object,name,color)

def ellipsoid(name,pos,size,color,sub=2):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=pos)
 ob=bind(bpy.context.object,name,color);ob.scale=size
 return ob

def rod(name,a,b,r,color,n=10,tip=None):
 a,b=Vector(a),Vector(b);d=b-a
 if d.length<.00001:return None
 ob=cyl(name,(a+b)*.5,r,d.length,color,n,tip)
 ob.rotation_euler=d.to_track_quat("Z","Y").to_euler()
 return ob

def hoop(name,pos,R,r,color,n=32,axis="Z"):
 bpy.ops.mesh.primitive_torus_add(major_segments=n,minor_segments=6,
  location=pos,major_radius=R,minor_radius=r)
 o=bind(bpy.context.object,name,color)
 if axis=="Y":o.rotation_euler.x=math.pi/2
 if axis=="X":o.rotation_euler.y=math.pi/2
 return o

def revolve(name,profile,color,sides=36):
 """Radial profile bottom-to-top, optionally returning along the interior wall."""
 v=[(r*math.cos(i*math.tau/sides),r*math.sin(i*math.tau/sides),z)
    for r,z in profile for i in range(sides)]
 f=[]
 for j in range(len(profile)-1):
  for i in range(sides):
   x=j*sides+i;y=j*sides+(i+1)%sides
   f.append((x,y,y+sides,x+sides))
 f.append(tuple(range(sides-1,-1,-1)))
 f.append(tuple((len(profile)-1)*sides+i for i in range(sides)))
 return mesh(name,v,f,color)

def polygon(name,points,color,depth=.018):
 """Extrude an arbitrary mostly planar polygon along Y (for front-facing pieces)."""
 n=len(points)
 v=[(x,y-depth/2,z) for x,y,z in points]+[(x,y+depth/2,z) for x,y,z in points]
 f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
 for i in range(n):
  j=(i+1)%n;f.append((i,j,j+n,i+n))
 return mesh(name,v,f,color)

def strand(name,points,color,r=.02,n=8):
 """Continuous segment chain with shared bevel-style round pieces."""
 for j in range(len(points)-1):
  rod(name+"_%02d"%j,points[j],points[j+1],r,color,n)

def petals(name,c,z,r,color="gold",count=5,y=-.02):
 x=c
 for j in range(count):
  a=j*math.tau/count
  ellipsoid(name+"_petal%02d"%j,(x+r*math.cos(a),y,z+r*math.sin(a)),
            (.068,.025,.11),color)
 ellipsoid(name+"_center",(x,y-.012,z),(.06,.033,.06),"vermilion")

def ribs(name,count,r,z0,z1,color="hinoki",width=.013):
 for i in range(count):
  a=i*math.tau/count
  rod(name+str(i),(r*math.cos(a),r*math.sin(a),z0),
      (r*math.cos(a),r*math.sin(a),z1),width,color,8)

def ringdots(name,count,r,z,color="gold",sz=.028):
 for j in range(count):
  a=j*math.tau/count
  ellipsoid(name+str(j),(r*math.cos(a),r*math.sin(a),z),(sz,sz,sz),color,1)

def lattice(name,w,h,z,cols,rows,color="hinoki",y=-.01):
 for j in range(cols+1):
  x=-w/2+w*j/cols
  rod(name+"_v"+str(j),(x,y,z-h/2),(x,y,z+h/2),.014,color,6)
 for j in range(rows+1):
  h0=z-h/2+h*j/rows
  rod(name+"_h"+str(j),(-w/2,y,h0),(w/2,y,h0),.014,color,6)

def textile(name,pos,sz,color,folds=10):
 x0,y0,z0=pos;w,d,h=sz
 box(name+"cloth",pos,sz,color,.016)
 for j in range(1,folds):
  x=x0-w/2+j*w/folds
  rod(name+"_stitch"+str(j),(x,y0-d*.52,z0-h*.48),
      (x,y0-d*.52,z0+h*.48),.006,"washi",6)

def braids(name,r,zlo,zhi,n=9,col="straw"):
 for j in range(n):
  phase=j*math.tau/n;pts=[]
  for k in range(11):
   a=phase+k*.28
   pts.append((r*math.cos(a),r*math.sin(a),zlo+(zhi-zlo)*k/10))
  strand(name+str(j),pts,col,.012,6)

def radial(name,number,r0,r1,z,color):
 for j in range(number):
  a=j*math.tau/number
  rod(name+str(j),(r0*math.cos(a),r0*math.sin(a),z),
      (r1*math.cos(a),r1*math.sin(a),z),.018,color,8)

def legs(name,r,zlo,zhi,number,color="wooddark"):
 for j in range(number):
  a=(j+.5)*math.tau/number
  rod(name+str(j),(r*math.cos(a),r*math.sin(a),zlo),
      (r*.83*math.cos(a),r*.83*math.sin(a),zhi),.07,color)
