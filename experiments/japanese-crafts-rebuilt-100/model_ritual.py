"""Ceremonial objects: rope, crested textiles, paper streamers, wood ornaments."""
import math
from geometry import *
def make(i):
 if i==0:
  polygon("Hand-cut wooden ema pentagonal shrine plaque",[(-.56,0,.30),(.56,0,.30),(.56,0,1.14),(0,0,1.47),(-.56,0,1.14)],"hinoki",.10)
  ellipsoid("Ema hanging hole",(0,-.06,1.34),(.058,.020,.06),"wooddark")
  strand("Red hanging cord",[(-.09,0,1.35),(-.10,0,1.68),(0,0,1.81),(.10,0,1.68),(.09,0,1.35)],"red",.027)
  polygon("Ema painted horse", [(-.28,-.06,.62),(.06,-.06,.66),(.27,-.06,.85),(.14,-.06,1.02),(-.19,-.06,.96)],"red",.02)
  for x in (-.16,.14):rod("Horse raised leg",(x,-.065,.68),(x,-.065,.49),.028,"wooddark")
 elif i==1:
  polygon("Precisely pointed omamori silk pouch",[(-.41,0,.28),(.41,0,.28),(.41,0,1.21),(0,0,1.48),(-.41,0,1.21)],"red",.12)
  for s in (-1,1):
   strand("Omamori raised side stitching",[(s*.38,-.07,.31),(s*.38,-.07,1.15),(0,-.07,1.43)],"gold",.016)
  hoop("Woven closure cord",(0,0,1.50),.13,.037,"gold",18,"Y")
  box("Central charm protective stitch",(0,-.077,.77),(.21,.02,.45),"gold",.012)
  for k in range(6):ellipsoid("Decorative silk dot",(-.27+k*.11,-.078,.39),(.015,.010,.02),"ivory",1)
 elif i==2:
  # Two visibly twisted strands in a large hand-tied shimenawa ring.
  for j in range(3):
   points=[]
   for k in range(121):
    t=k*math.tau/120
    r=.70+.055*math.cos(12*t+j*math.tau/3)
    x=r*math.cos(t);z=.99+r*math.sin(t)
    points.append((x,-.01+.055*math.sin(12*t+j*math.tau/3),z))
   strand("Twisted rice straw rope",points,"straw" if j%2 else "hinoki",.055,8)
  for x in (-.45,0,.45):
   polygon("Shimenawa white shide",[(x-.08,-.10,.42),(x+.09,-.10,.42),
     (x+.09,-.10,.17),(x+.25,-.10,.17),(x+.25,-.10,.01),(x-.08,-.10,.01)],"washi",.02)
 elif i==3:
  cyl("Kagura suzu wooden hand grip",(0,0,.32),.076,.65,"cedar",18)
  rod("Ornamental brass branch",(0,0,.53),(0,0,1.62),.06,"gold",18)
  for tier,r,z in [(0,.32,.79),(1,.27,1.09),(2,.21,1.37)]:
   for j in range(7-tier):
    a=j*math.tau/(7-tier)
    x,y=r*math.cos(a),r*math.sin(a)
    rod("Suzu branch",(0,0,z-.12),(x,y,z),.024,"bronze")
    ellipsoid("Distinct individually cast suzu bell",(x,y,z),(.115,.115,.11),"gold",2)
    hoop("Bell opening",(x,y,z-.11),.058,.012,"iron",12)
 elif i==4:
  polygon("Long omikuji folded fortune", [(-.20,0,.11),(.20,0,.11),(.20,0,1.52),(-.20,0,1.52)],"washi",.024)
  for j in range(14):
   z=.18+j*.09
   box("Calligraphic fortune line",(0,-.02,z),(.18,.012,.018),"black",.002)
  for j in range(3):
   box("Accordion folded corner",(0,-.04,.27+j*.14),(.35,.020,.028),"red",.003)
  ellipsoid("Red seal",(0,-.022,1.37),(.095,.014,.083),"red")
 elif i==5:
  rod("Gohei polished wooden staff",(0,0,.02),(0,0,1.87),.063,"cedar",18)
  for s in (-1,1):
   for j in range(6):
    z=.83+j*.15
    polygon("Gohei precisely stepped white streamer",[(s*.08,0,z),(s*.45,0,z+.13),
      (s*.45,0,z-.04),(s*.60,0,z-.04),(s*.60,0,z-.19),(s*.24,0,z-.19)],
      "washi",.018)
  hoop("Red silk binding",(0,0,1.77),.068,.024,"red")
 elif i==6:
  rod("Hamaya ritual white arrow",(0,0,.09),(0,0,1.91),.037,"hinoki",18)
  cyl("Hamaya pointed gold arrowhead",(0,0,1.95),.09,.29,"gold",8,0)
  for s in (-1,1):
   polygon("Feather fletching with notched edge",[(0,0,.27),(s*.26,0,.65),(s*.17,0,.82),(0,0,.80)],"ivory",.032)
   for j in range(5):rod("Feather spines",(0,-.02,.33+j*.09),(s*(.10+.02*j),-.02,.51+j*.04),.01,"wooddark")
  for z in (.79,.86):hoop("Arrow fletching binding",(0,0,z),.045,.013,"red")
 elif i==7:
  rod("Shide sacred bamboo crossbar",(-1.12,0,1.72),(1.12,0,1.72),.052,"cedar",18)
  for j in range(5):
   x=-.82+j*.40
   polygon("Shide folded zigzag paper",[(x-.13,0,1.68),(x+.12,0,1.68),(x+.12,0,1.38),
    (x+.28,0,1.38),(x+.28,0,1.10),(x+.12,0,1.10),
    (x+.12,0,.82),(x-.06,0,.82),(x-.06,0,1.1),
    (x-.13,0,1.1)],"washi",.020)
   rod("Binding thread",(x,0,1.68),(x,0,1.81),.013,"red")
 elif i==8:
  box("Carved square wooden masu",(0,0,.45),(.98,.96,.88),"hinoki",.038)
  box("Visible deep black cup interior",(0,0,.902),(.77,.75,.010),"wooddark",.001)
  for x in (-.45,.45):
   box("Masu interlocking wooden joinery",(x,0,.74),(.105,.97,.11),"cedar",.006)
  for y in (-.43,.43):
   box("Masu top end-grain",(0,y,.90),(.98,.09,.08),"cedar",.006)
  petals("Masu burn-stamped mark",0,.52,.13,"wooddark",5,y=-.49)
 elif i==9:
  box("Sanbo offering tray",(0,0,.08),(1.46,1.02,.16),"cedar",.036)
  ellipsoid("Lower kagami mochi", (0,0,.41),(.59,.56,.29),"ivory",3)
  ellipsoid("Upper kagami mochi",(0,0,.78),(.44,.42,.23),"washi",3)
  ellipsoid("Japanese daidai citrus",(0,0,1.05),(.22,.22,.21),"orange",3)
  ellipsoid("Daidai leaf",(.15,0,1.27),(.21,.12,.047),"green")
  for x in (-.53,.53):box("Red-and-white offering strips",(x,-.43,.18),(.22,.10,.39),"red",.02)
