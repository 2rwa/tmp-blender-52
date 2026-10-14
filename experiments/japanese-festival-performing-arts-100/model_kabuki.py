"""Kabuki motifs, actors' brocade costume, tools and theatrical fittings."""
import math
from geometry import *
from parts import *
def make(i):
 if i==0:
  mask("Kumadori exaggerated stage face",style=5,color="ivory")
  for s in (-1,1):
   for k in range(3):
    strand("Red kumadori flame eye line",[(s*.09,-.44,1.35-k*.14),
      (s*.27,-.45,1.33-k*.11),(s*.43,-.32,1.53-k*.10)],"red",.029)
  for j in range(6):
   x=-.25+j*.10
   rod("Bared ivory teeth",(x,-.43,.79),(x,-.44,.72),.030,"ivory")
 elif i==1:
  fan("Kabuki fan for mie pose",36,"red")
  for j in range(14):
   a=-.82+j*.125
   strand("Embroidered kabuki gilt arc",[(.70*math.sin(a),-.04,.18+.7*math.cos(a)),
   (1.07*math.sin(a),-.04,.18+1.07*math.cos(a))],"gold",.013)
 elif i==2:
  costume("Hikinuki double layered kabuki costume","red","gold")
  # removable-looking separate upper garment
  for s in (-1,1):
   polygon("Hidden blue reveal robe panel",[(s*.36,-.095,.3),(s*.92,-.095,.49),
      (s*.94,-.095,1.06),(s*.36,-.095,1.16)],"blue",.043)
   for j in range(8):
    z=.36+j*.11
    ellipsoid("Hikinuki decorative mirror motif",(s*.70,-.13,z),(.05,.022,.052),"ivory",1)
  strand("Pull-release costume rigging",[(-.48,.05,1.40),(0,.11,1.88),(.48,.05,1.40)],"ivory",.018)
 elif i==3:
  revolve("Bamboo theatre kasa silhouette",[(.02,.38),(.24,.43),(.68,.57),(1.07,.84),(.12,.92)],"straw",36)
  for j in range(30):
   a=j*T/30
   rod("Bamboo kasa spoke",(0,0,.92),(1.03*math.cos(a),1.03*math.sin(a),.84),.015,"cedar")
  hoop("Silk kasa brim",(0,0,.84),1.07,.029,"red")
  strand("Silk chin strap",[(-.42,0,.56),(-.28,0,.10),(.28,0,.10),(.42,0,.56)],"indigo",.026)
 elif i==4:
  for s in (-1,1):
   box("Stage hyoshigi solid hardwood striking block",(s*.19,0,.82),(.21,.31,1.44),"hinoki",.048)
   for j in range(10):
    z=.24+j*.12
    rod("Hyoshigi wood-grain cut",(s*.19-.09,-.17,z),(s*.19+.09,-.17,z),.009,"cedar")
  strand("Hyoshigi paired instrument connecting cord",[(-.19,0,1.55),(0,0,1.84),(.19,0,1.55)],"red",.03)
 elif i==5:
  box("Kabuki tsukeita resonant stage board",(0,0,.18),(1.64,.94,.23),"cedar",.03)
  for s in (-1,1):
   rod("Tsukeita clapping block",(s*.38,-.25,.39),(s*.15,-.25,1.26),.064,"hinoki")
  for x in (-.68,-.3,.08,.46):box("Board wood plank visible seam",(x,0,.305),(.026,.90,.018),"wooddark")
 elif i==6:
  revolve("Black kurogo stage head covering",[(.22,.18),(.40,.27),(.45,.91),(.31,1.55),(.1,1.66)],"black")
  ellipsoid("Face blackout panel",(0,-.42,1.12),(.32,.07,.39),"charcoal")
  for j in range(12):
   x=-.28+j*.051
   rod("Cloth folds",(x,-.435,.88),(x,-.435,1.41),.008,"wooddark")
  strand("Back kurogo tied sash",[(-.25,.25,.41),(0,.54,.65),(.25,.25,.41)],"black",.04)
 elif i==7:
  lantern("Kabuki playhouse named red lantern",0,0,1.07,1.54,"red")
  for j in range(5):
   z=.73+j*.17
   box("Gold calligraphy accent",(0,-.43,z),(.16,.03,.046),"gold",.006)
 elif i==8:
  for x in (-.30,0,.30):
   rod("Ornate kanzashi hair stick",(x,0,.14),(x*.8,0,1.58),.041,"gold")
   flower("Kabuki onnagata kanzashi flower",(x*.8,-.07,1.57),.17,"pink",8)
   for j in range(7):
    a=j*T/7
    strand("Dangling fine gold pin ornament",[(x*.8+.13*math.cos(a),-.08,1.45),
        (x*.8+.13*math.cos(a),-.09,1.00)],"gold",.015)
 elif i==9:
  rod("Long kiseru bamboo shaft",(-1.09,0,.30),(.96,0,.43),.046,"bamboo")
  cyl("Silver kiseru stem ferrule",(-.90,0,.31),.055,.16,"steel",16).rotation_euler.y=math.pi/2
  rod("Cast copper smoking bowl",(.85,0,.41),(1.05,0,.67),.10,"bronze",16)
  revolve("Kiseru tiny open bowl",[(.02,.0),(.09,.03),(.12,.12),(.09,.16)],"bronze",20).location=(1.05,0,.67)
