import math
import bpy
from geometry import *
def lathe(name,profile,color,sides=18):
 verts=[(r*math.cos(2*math.pi*i/sides),r*math.sin(2*math.pi*i/sides),z) for r,z in profile for i in range(sides)]
 faces=[]
 for j in range(len(profile)-1):
  for i in range(sides):
   p=j*sides+i;q=j*sides+(i+1)%sides;faces.append((p,q,q+sides,p+sides))
 faces.extend([tuple(range(sides-1,-1,-1)),tuple((len(profile)-1)*sides+i for i in range(sides))])
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);return bind(o,name,color)
