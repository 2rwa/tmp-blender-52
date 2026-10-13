from geometry import *
def make(i):
 if i==0:
  box("Inkstone",(0,0,.18),(.82,1.28,.30),"iron")
  box("Inkstone reservoir",(0,.30,.337),(.59,.40,.024),"black")
  box("Grinding surface",(0,-.20,.343),(.61,.63,.018),"gray")
 elif i==1:
  rod("Brush handle",(0,0,.42),(0,0,1.55),.065,"bamboo")
  cyl("Brush ferrule",(0,0,.36),.092,.16,"gold")
  cyl("Calligraphy brush tip",(0,0,.17),.08,.33,"black",12,0)
 elif i==2:
  box("Sumi inkstick",(0,0,.12),(.38,.96,.24),"black")
  box("Inkstick gilded emboss",(0,-.1,.245),(.12,.51,.015),"gold")
 elif i==3:
  rod("Bunchin paperweight",(-.82,0,.14),(.82,0,.14),.115,"iron",12)
  for x in (-.61,.61):ring("Gold carved end",(x,0,.14),.114,.017,"gold",12,"X")
 elif i==4:
  box("Unrolled scroll",(0,0,.18),(1.20,.90,.035),"paper")
  for x in (-.61,.61):cyl("Makimono scroll rod",(x,0,.18),.11,.99,"wood",12).rotation_euler[0]=1.570796
  for j in range(5):box("Calligraphic mark",(-.42+j*.20,-.1,.22),(.07,.29,.012),"black")
 elif i==5:
  for j in range(5):box("Handmade washi sheet",(.015*j,.02*j,.08+j*.018),(1.1,1.45,.018),"paper")
  for j in range(6):orb("Paper fiber",(-.4+j*.15,-.2,.19),(.03,.06,.01),"gray")
 elif i==6:
  box("Suzuribako lacquer box",(0,0,.23),(.99,.73,.43),"black")
  box("Suzuribako lid",(0,0,.47),(1.05,.79,.09),"red")
  orb("Makie gold motif",(0,-.02,.52),(.21,.16,.015),"gold")
 elif i==7:
  cyl("Hanko stamp body",(0,0,.40),.19,.80,"wood2",12)
  cyl("Seal end",(0,0,.05),.23,.11,"red",12)
  ring("Lacquer ring",(0,0,.77),.18,.015,"gold")
 elif i==8:
  for j in range(3):box("Inro lacquer compartment",(0,0,.22+j*.23),(.69,.45,.20),"indigo")
  for z in (.33,.56):box("Fine makie band",(0,-.23,z),(.70,.025,.028),"gold")
  bend("Inro silk cord",[(0,0,.8),(.28,0,1.02),(.1,0,1.30)],"red",.024)
 else:
  box("Kakejiku paper scroll",(0,0,.81),(.95,.024,1.19),"paper")
  for z in (.18,1.45):rod("Scroll dowel",(-.56,0,z),(.56,0,z),.05,"wood")
  orb("Landscape mountain",(0,-.023,.85),(.31,.03,.25),"indigo")
  rod("Scroll cord",(0,0,1.49),(0,0,1.75),.022,"red")
