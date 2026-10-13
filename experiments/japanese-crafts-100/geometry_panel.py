import math
import bpy
from geometry import *
def panel(name,points,color):
 mesh=bpy.data.meshes.new(name)
 mesh.from_pydata(points,[],[tuple(range(len(points)))])
 mesh.update()
 o=bpy.data.objects.new(name,mesh)
 bpy.context.collection.objects.link(o)
 return bind(o,name,color)
def fan(name,z,r,n,color):
 for i in range(n):
  a=math.pi*i/n;b=math.pi*(i+1)/n
  panel(name+str(i),[(0,0,z),(r*math.cos(a),0,z+r*math.sin(a)),(r*math.cos(b),0,z+r*math.sin(b))],color if i%2 else "paper")
  rod(name+str(i),(0,0,z),(r*math.cos(a),0,z+r*math.sin(a)),.012,"wood2",6)
