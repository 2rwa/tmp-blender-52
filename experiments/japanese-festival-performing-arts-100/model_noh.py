"""Noh masks, stage panel, brocade and hayashi instruments."""
import math
from geometry import *
from parts import *
def pine_panel(name):
 box(name+" broad cedar frame",(0,0,1.02),(1.72,.13,1.88),"wooddark")
 box(name+" gold-tinted washed plaster",(0,-.09,1.03),(1.59,.04,1.69),"washi")
 strand(name+" ancient bent pine trunk",[(-.60,-.13,.19),(-.39,-.14,.62),(-.29,-.16,1.20),
     (-.06,-.16,1.45),(.34,-.17,1.50),(.60,-.18,1.72)],"wooddark",.12)
 for j in range(19):
  a=j*T/19
  z=1.33+.43*math.sin(a)
  rod(name+" sprawling pine branch",(-.18,-.18,1.25),
     (.65*math.cos(a),-.18,z),.03,"wooddark")
  for k in range(5):
   ellipsoid(name+" pine needle tuft",(.64*math.cos(a)+(k-2)*.052,-.20,z+.025*k),
          (.07,.026,.028),"green",1)
 for s in (-1,1):box(name+" support foot",(s*.67,0,.06),(.25,.59,.12),"cedar")
def make(i):
 if i in (0,1,2,3):
  mask("Noh hand carved "+str(i),style={0:0,1:1,2:0,3:2}[i],
       color=["ivory","ivory","washi","vermilion"][i])
  if i==1:
   for s in (-1,1):
    rod("Long hannya horns",(s*.27,0,1.60),(s*.44,0,2.06),.10,"ivory",14,0)
    strand("Hannya brow horror ridge",[(s*.15,-.45,1.39),
          (s*.33,-.47,1.41),(s*.40,-.42,1.24)],"red",.039)
  elif i==2:
   ellipsoid("Okina flowing white beard",(0,-.29,.56),(.32,.12,.33),"washi",3)
   for j in range(16):
    x=-.28+j*.037
    strand("Articulated white beard tassel",[(x,-.31,.55),(x+.04,-.29,.08)],"ivory",.012)
  elif i==0:
   for s in (-1,1):
    strand("Koomote delicate eye accent",[(s*.1,-.42,1.25),(s*.27,-.40,1.23)],"charcoal",.012)
 elif i==4:fan("Noh painted folding fan",32,"gold")
 elif i in (5,6):
  z=.87;R=.33 if i==5 else .45;length=.68 if i==5 else .93
  drum("Tsuzumi hourglass multi-strand hand drum",(0,0,z),R,length,"Y","red",True)
  for j in range(22):
   a=T*j/22
   strand("Hourglass tsuzumi cross cord",[(R*math.cos(a),-.48,z+R*math.sin(a)),
    ((R*.55)*math.cos(a),0,z+(R*.55)*math.sin(a)),
    (R*math.cos(a+.3),.48,z+R*math.sin(a+.3))],"red",.020)
  for s in (-1,1):hoop("Tsuzumi lashing flange",(0,s*length*.5,z),R,.04,"gold",24,"Y")
 elif i==7:
  rod("Nohkan decorated transverse flute",(-1.25,0,.26),(1.25,0,.26),.091,"wooddark",24)
  for j in range(18):
   x=-1.18+j*.131
   hoop("Nohkan bark wrapping",(x,0,.26),.095,.013,"gold",20,"X")
  for x in [-.77,-.61,-.43,-.27,-.09,.11,.35,.52]:
   ellipsoid("Nohkan blowing aperture",(x,-.09,.25),(.045,.016,.045),"black")
 elif i==8:
  costume("Rich brocade karaori noh robe","red","gold")
  for j in range(9):
   x=-.3+j*.075
   for k in range(10):
    z=.27+k*.12
    if (k+j)%3==0:flower("Gold kikkou woven silk",(x,-.17,z),.041,"gold")
  for x in (-.72,.72):fringe("Rich karaori sleeve tassels",x,0,.51,.39,9,"gold")
 elif i==9:pine_panel("Noh stage painted kagamiita")
