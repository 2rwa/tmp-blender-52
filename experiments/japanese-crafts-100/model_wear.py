import math
from geometry import *
from geometry_panel import fan
def make(i):
 if i==0:
  fan("Sensu folding fan",.36,.96,16,"red")
  rod("Decorative handle",(0,0,.04),(0,0,.35),.06,"wood")
 elif i==1:
  orb("Uchiwa paper face",(0,0,1.0),(.65,.045,.62),"paper",2)
  rod("Uchiwa bamboo handle",(0,0,.06),(0,0,.75),.055,"bamboo")
  for j in range(7):rod("Rib",(0,0,.7),(.50*math.cos(math.pi*j/6),0,.96+.20*math.sin(math.pi*j/6)),.012,"wood")
 elif i==2:
  cyl("Wagasa central shaft",(0,0,.88),.075,1.77,"bamboo")
  for j in range(16):
   a=j*math.tau/16;b=(j+1)*math.tau/16
   from geometry_panel import panel
   panel("Umbrella canopy",[(0,0,1.66),(.93*math.cos(a),.93*math.sin(a),1.24),(.93*math.cos(b),.93*math.sin(b),1.24)],"red" if j%2 else "paper")
   rod("Canopy rib",(0,0,1.66),(.93*math.cos(a),.93*math.sin(a),1.24),.014,"wood2")
 elif i==3:
  for x in (-.35,.35):
   box("Geta sandal platform",(x,0,.33),(.52,1.02,.13),"wood2")
   for y in (-.25,.28):box("Geta foot",(x,y,.16),(.45,.16,.31),"wood")
   bend("Hanao strap",[(x-.19,-.08,.43),(x,.17,.59),(x+.19,-.08,.43)],"red",.052)
 elif i==4:
  for x in (-.32,.32):
   orb("Zori straw sole",(x,0,.10),(.25,.52,.10),"bamboo",2)
   bend("Thong strap",[(x-.16,-.12,.16),(x,.18,.35),(x+.16,-.12,.16)],"red",.04)
 elif i==5:
  for x in (-.32,.32):
   orb("Tabi ankle",(x,.12,.40),(.23,.20,.38),"white")
   orb("Tabi foot",(x,-.17,.13),(.27,.39,.15),"white")
   orb("Split toe",(x-.11,-.48,.12),(.12,.16,.10),"paper")
 elif i==6:
  rod("Ornamental hairpin",(-.72,0,.18),(.55,0,1.42),.035,"gold")
  for j in range(5):orb("Cherry blossom petal",(.55+.19*math.cos(j*math.tau/5),0,1.42+.19*math.sin(j*math.tau/5)),(.13,.055,.15),"pink")
  orb("Flower center",(.55,-.05,1.42),(.075,.05,.075),"gold")
 elif i==7:
  orb("Kinchaku cloth bag",(0,0,.55),(.54,.43,.56),"indigo",2)
  ring("Drawstring rim",(0,0,1.01),.35,.035,"gold")
  bend("Drawstring loop",[(-.29,0,1.04),(-.40,0,1.45),(0,0,1.52),(.40,0,1.45),(.29,0,1.04)],"red",.025)
 elif i==8:
  box("Wrapped furoshiki package",(0,0,.35),(.97,.87,.70),"wood2")
  for a in (-.18,.18):box("Cross folded cloth",(a,0,.73),(.27,.90,.13),"blue")
  bend("Knot",[(-.14,0,.78),(-.15,0,1.03),(0,0,.95),(.16,0,1.03),(.16,0,.78)],"blue",.07)
 else:
  box("Tenugui hanging cotton",(0,0,.70),(1.52,.04,1.22),"paper")
  for j in range(5):box("Indigo dyed stripe",(-.60+j*.30,-.035,.71),(.095,.023,.96),"indigo")
  rod("Hanging dowel",(-.85,0,1.36),(.85,0,1.36),.035,"wood")
