"""Regional and fine crafts: metal casting, lacquerware, kiriko, cords."""
import math
from geometry import *
def make(i):
 if i==0:
  revolve("Cast bronze koro incense burner",[(.29,.14),(.52,.17),(.62,.34),(.64,.70),(.55,.91),(.38,.96)],"bronze",40)
  cyl("Removable koro openwork lid",(0,0,.96),.49,.11,"iron",36)
  ellipsoid("Lotus finial",(0,0,1.09),(.15,.15,.13),"gold")
  legs("Koro three mythical tripod feet",.41,.06,.28,3,"gold")
  for j in range(16):
   a=j*math.tau/16
   ellipsoid("Pierced lid lattice window",( .38*math.cos(a),.38*math.sin(a),1.022),
             (.035,.034,.014),"gold",1)
  for z in (.34,.56,.79):hoop("Fine chased bronze band",(0,0,z),.64,.023,"gold")
 elif i==1:
  revolve("Orin brass resonating lip",[(.18,.08),(.42,.14),(.55,.41),(.59,.60),(.52,.67),(.45,.59),(.38,.30),(.17,.17)],"gold",40)
  cyl("Vermilion woven ring cushion",(0,0,.09),.43,.16,"red",28)
  hoop("Engraved bell upper rim",(0,0,.645),.55,.031,"bronze",40)
  rod("Singing bowl turned wooden mallet",(-.87,0,.09),(-.30,0,.75),.075,"cedar",18)
  ellipsoid("Orin felt-covered beater",(-.27,0,.78),(.14,.14,.17),"fabric")
 elif i==2:
  ellipsoid("Carved elliptical mokugyo walnut",(0,0,.65),(.69,.51,.57),"cedar",3)
  ellipsoid("Mokugyo open fish-mouth hollow",(0,-.499,.60),(.48,.045,.21),"wooddark")
  for j in range(9):
   a=j*math.pi/10
   rod("Fish scale carving",( -.45+.10*j,-.50,.77),(-.44+.10*j,-.51,.92),.022,"hinoki")
  ellipsoid("Twisted carved tail",(.53,0,.79),(.21,.32,.20),"cedar")
  rod("Rounded mallet shaft",(-.80,0,.15),(-.31,0,.92),.075,"hinoki")
  ellipsoid("Fabric covered mallet head",(-.30,0,.94),(.20,.18,.17),"fabric")
 elif i==3:
  revolve("Twelve-facet kiriko glass body",[(.26,.05),(.34,.06),(.48,.87),(.51,1.14),(.47,1.18),(.41,1.12),(.37,.92),(.24,.14)],"blue",12)
  for k in range(7):
   z=.18+k*.145;r=.32+(.15*k/7)
   hoop("Diamond cut lower edges",(0,0,z),r,.022,"ivory",12)
  for j in range(12):
   a=j*math.tau/12
   strand("Kiriko etched V-cut ridge",[(.31*math.cos(a),.31*math.sin(a),.20),
    (.44*math.cos(a+.18),.44*math.sin(a+.18),.57),
    (.47*math.cos(a),.47*math.sin(a),1.09)],"ivory",.015)
 elif i==4:
  revolve("Shikki wan carved lacquer rice bowl",[(.25,.05),(.42,.10),(.56,.23),(.65,.59),(.61,.66),(.53,.62),(.43,.30),(.18,.16)],"red",40)
  hoop("Gold hand-laid rim",(0,0,.637),.622,.029,"gold",40)
  revolve("Elevated black lacquer bowl foot",[(.18,.015),(.27,.02),(.28,.095),(.24,.13)],"lacquer")
  petals("Gold shikki lacquer painting",0,.46,.14,"gold",6,y=-.61)
 elif i==5:
  box("High-gloss makie box carcass",(0,0,.36),(1.30,.87,.60),"lacquer",.10)
  box("Makie independent inset lid",(0,0,.695),(1.35,.93,.12),"red",.065)
  for x in (-.59,.59):box("Thin gilt trim",(x,0,.76),(.028,.90,.017),"gold",.003)
  for y in (-.40,.40):box("Gilt horizontal trim",(0,y,.76),(1.28,.024,.018),"gold",.003)
  petals("Gold makie plum flower",-.19,.77,.20,"gold",7,y=-.15)
  for j in range(25):
   a=j*math.tau/25
   ellipsoid("Tiny makie gold dust",(.32+.20*math.cos(a),.20*math.sin(a),.758),
             (.013,.013,.009),"gold",1)
 elif i==6:
  ellipsoid("Kabuto steel domed helmet shell",(0,0,.74),(.58,.45,.49),"iron",3)
  for s in (-1,1):
   polygon("Kabuto flaring articulated cheek guard",[(s*.37,0,.68),(s*.59,0,.62),
     (s*.77,0,.35),(s*.46,0,.30)],"red",.080)
   polygon("Golden sweeping warrior horn",[(s*.24,0,1.08),(s*.63,0,1.33),
    (s*.75,0,1.61),(s*.46,0,1.47)],"gold",.09)
  for k in range(4):
   z=.33+k*.12
   hoop("Armor lamellar neckguard",(0,0,z),.58+.06*(3-k),.028,"lacquer",32)
  ellipsoid("Helmet gold center crest",(0,-.47,1.11),(.19,.08,.18),"gold")
  box("Black ceremonial helmet display",(0,0,.08),(1.65,1.05,.16),"wooddark")
 elif i==7:
  cyl("Kazaridaru wooden barrel with barrel stave texture",(0,0,.66),.63,1.29,"cedar",40)
  ribs("Individual long sake cask staves",36,.632,.07,1.26,"hinoki",.018)
  for z in (.14,.38,.95,1.19):hoop("Thick braided sake cask rope",(0,0,z),.645,.045,"straw",40)
  box("Front white decorative sake barrel wrapping",(0,-.641,.64),(.64,.025,.79),"washi",.006)
  ellipsoid("Red stamped sake symbol",(0,-.672,.66),(.18,.017,.24),"red")
  cyl("Polished barrel head",(0,0,1.30),.64,.09,"hinoki",36)
 elif i==8:
  revolve("Tin sake serving flask",[(.21,.04),(.35,.09),(.43,.31),(.39,.77),(.24,.91),(.20,1.20),(.25,1.26),(.21,1.30)],"steel",32)
  rod("Slender curving pouring neck",(-.17,0,1.08),(-.58,0,1.22),.10,"steel",20)
  hoop("Hammered tin rim",(0,0,1.29),.24,.024,"ivory")
  for z in (.21,.39,.55,.73):hoop("Etched sake flask decoration",(0,0,z),.4,.012,"charcoal")
  for s in (-1,1):hoop("Carafe decorative bail",(s*.31,0,.80),.12,.024,"bronze",18,"Y")
 elif i==9:
  for j in range(12):
   phi=j*math.tau/12
   pts=[]
   for k in range(34):
    t=k/33; a=phi+math.tau*t*2.0
    rr=.39+.075*math.cos(a*3+j)
    pts.append((rr*math.cos(a),rr*math.sin(a),.08+1.4*t))
   strand("Individual silk kumihimo braid %02d"%j,pts,
          ["red","gold","indigo","washi"][j%4],.027,8)
  hoop("Braided kumihimo tassel collar",(0,0,1.47),.36,.055,"gold",32)
  for j in range(20):
   a=j*math.tau/20
   rod("Loose silk fringe tail",(.29*math.cos(a),.29*math.sin(a),.08),
       (.4*math.cos(a),.4*math.sin(a),-.23),.019,"red" if j%2 else "gold",6)
