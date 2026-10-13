"""Joinery-focused Japanese furniture and architectural miniatures."""
import math
from geometry import *
def make(i):
 if i==0:
  box("Tansu constructed solid wooden carcass",(0,0,.86),(1.46,.68,1.62),"cedar",.045)
  for j in range(5):
   z=.22+j*.29
   box("Individual removable tansu drawer",(0,-.355,z),(1.32,.075,.255),"hinoki",.022)
   for x in (-.47,.47):
    hoop("Forged circular drawer pull",(x,-.413,z),.068,.015,"iron",16,"X")
   box("Drawer top joinery lip",(0,-.392,z+.116),(1.34,.033,.018),"wooddark",.005)
  for x in (-.67,.67):
   box("Black metal corner band",(x,-.36,1.56),(.10,.02,.16),"iron",.007)
  for z in (.16,1.63):box("Tansu endgrain frame",(0,-.35,z),(1.49,.05,.07),"wooddark",.009)
 elif i==1:
  cyl("Solid circular chabudai tabletop",(0,0,.73),.95,.16,"hinoki",40)
  hoop("Finely milled chabudai edge",(0,0,.79),.93,.025,"cedar",40)
  for a in (.25,.75,1.25,1.75):
   angle=a*math.pi
   rod("Foldable wooden chabudai leg",(.52*math.cos(angle),.52*math.sin(angle),.06),
    (.60*math.cos(angle),.60*math.sin(angle),.67),.091,"cedar",12)
   ellipsoid("Dark hinge pin",(.60*math.cos(angle),.60*math.sin(angle),.67),(.08,.08,.04),"iron")
  radial("Tabletop carved planks",20,.13,.85,.815,"wooddark")
 elif i==2:
  box("Zaisu reclining wooden seat",(0,0,.25),(1.19,1.07,.16),"cedar",.064)
  box("Soft zaisu woven seat cushion",(0,-.05,.38),(1.02,.90,.16),"fabric",.08)
  back=box("Fitted angle backrest",(0,.47,1.03),(1.13,.14,1.38),"hinoki",.035)
  back.rotation_euler.x=-.16
  for x in (-.50,.50):
   box("Curved chair side arm",(x,.01,.51),(.075,.78,.10),"cedar")
  for j in range(8):
   x=-.43+j*.12
   rod("Woven backrest textile line",(x,.35,.54),(x,.35,1.59),.012,"indigo")
 elif i==3:
  for x in (-.44,.44):
   for y in (-.36,.36):box("Kotatsu squat wooden support",(x,y,.24),(.14,.15,.47),"cedar")
  box("Warm quilt draped on kotatsu",(0,0,.57),(1.61,1.32,.86),"fabric",.09)
  for x in (-.70,.70):
   box("Kotatsu quilt decorative tassel border",(x,0,.28),(.095,1.33,.12),"red")
  box("Heavy polished kotatsu tabletop",(0,0,1.05),(1.64,1.35,.14),"hinoki",.055)
  for j in range(12):
   x=-.73+j*.13
   rod("Top cedar grain",(x,-.57,1.126),(x,.57,1.126),.008,"cedar",6)
 elif i==4:
  box("Massive joined nagamochi storage chest",(0,0,.60),(1.92,.82,1.10),"cedar",.045)
  box("Banded removable raised chest lid",(0,0,1.19),(2.04,.94,.12),"hinoki",.035)
  for x in (-.87,.87):
   hoop("Cast iron nagamochi carrying ear",(x,0,.62),.18,.045,"iron",22,"X")
   box("Metal reinforcement corner",(x,-.43,.54),(.085,.025,.79),"iron",.004)
  for j in range(3):
   x=-.68+j*.68
   box("Carved wooden chest plank",(x,-.426,.75),(.03,.033,.80),"hinoki")
 elif i==5:
  box("Tsuitate white rice-paper screen",(0,0,.97),(1.64,.055,1.59),"washi",.009)
  for x in (-.85,.85):box("Vertical main lacquer post",(x,0,1.0),(.095,.16,1.90),"wooddark")
  for z in (.13,1.88):box("Screen horizontal rail",(0,0,z),(1.79,.14,.075),"wooddark")
  for x in (-.68,.68):box("Freestanding screen wooden shoes",(x,0,.067),(.29,.87,.13),"cedar")
  lattice("Fine tsuitate screen shoji lattice",1.60,1.51,.98,8,7,"cedar",-.06)
 elif i==6:
  for x in (-.74,.74):box("Bookstand upright",(x,0,.99),(.10,.52,1.95),"cedar")
  for z in (.14,.64,1.14,1.64):
   box("Bookstand shelving plank",(0,0,z),(1.57,.56,.11),"hinoki",.023)
  for row,z in enumerate([.39,.88,1.38]):
   for j in range(7):
    x=-.58+j*.19
    box("Sewn book spine %d_%d"%(row,j),(x,-.03,z),(.14,.32,.39),
        ["indigo","red","washi"][j%3],.015)
    for zz in (z-.14,z+.13):
     box("Fine bound book tape",(x,-.20,zz),(.14,.022,.019),"gold")
 elif i==7:
  box("Fumikiri top wooden stepping platform",(0,0,.70),(1.01,.60,.14),"hinoki",.036)
  for x in (-.38,.38):
   box("Tapered legs",(x,0,.35),(.10,.52,.67),"cedar",.022)
  rod("Diagonal hardwood brace",(-.35,-.25,.18),(.34,-.25,.58),.030,"wooddark")
  for j in range(7):
   x=-.39+j*.13
   rod("Anti-slip carved top ridges",(x,-.25,.776),(x,.25,.776),.012,"cedar",6)
 elif i==8:
  revolve("Turned carved wooden serving tray",[(.20,.05),(.55,.07),(.79,.12),(.86,.22),(.81,.27),(.75,.21),(.47,.16),(.18,.16)],"hinoki",40)
  hoop("Ornamental obon raised edge",(0,0,.235),.818,.038,"cedar",40)
  radial("Visible natural cedar grain",24,.16,.71,.175,"cedar")
  petals("Tray engraved blossom",0,.18,.12,"red",6,y=-.02)
 elif i==9:
  box("Kumiko rectangular surrounding frame",(0,0,1.02),(1.61,.10,1.93),"wooddark",.032)
  box("Kumiko translucent white backing",(0,-.061,1.01),(1.44,.012,1.72),"washi",.001)
  lattice("Kumiko full tiny timber lattice",1.39,1.66,1.01,10,12,"cedar",-.078)
  for j in range(9):
   x=-.58+j*.145
   for k in range(11):
    z=.30+k*.14
    rod("Kumiko geometric diagonal",(x-.055,-.09,z-.055),(x+.055,-.09,z+.055),.009,"hinoki",6)
  box("Kumiko stand foot",(0,0,.055),(1.83,.45,.11),"cedar")
