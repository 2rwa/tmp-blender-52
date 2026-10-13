"""Tea ceremony: ten independently sculpted Japanese utensils."""
import math
from geometry import *
def make(i):
 if i==0: # tea bowl, thrown lip, foot ring, interior, glaze relief
  revolve("Tea bowl, thick rolled lip",[(.13,.08),(.25,.055),(.35,.08),(.51,.18),(.64,.46),(.67,.60),(.64,.65),(.58,.64),(.53,.48),(.38,.22),(.16,.15),(.02,.15)],"celadon")
  hoop("raised rim",(0,0,.625),.621,.034,"cream",40)
  hoop("carved foot",(0,0,.095),.28,.035,"clay")
  ringdots("speckled glaze",20,.62,.49,"clay",.018)
 elif i==1: # bamboo whisk
  cyl("Split-bamboo chasen handle",(0,0,.25),.14,.5,"bamboo",20)
  hoop("Hand-tied black cord",(0,0,.44),.145,.027,"indigo")
  for j in range(56):
   a=j*math.tau/56;u=(math.cos(a),math.sin(a))
   strand("Whisk bent tine%02d"%j,[(u[0]*.13,u[1]*.13,.49),
     (u[0]*.18,u[1]*.18,.64),(u[0]*.40,u[1]*.40,.92),
     (u[0]*.37,u[1]*.37,1.16),(u[0]*.23,u[1]*.23,1.28)],"bamboo",.009,6)
 elif i==2: # chashaku
  strand("Bamboo long shaft",[(-.75,0,.10),(-.36,0,.13),(.06,0,.19),(.40,0,.21),(.55,0,.18)],"bamboo",.05)
  ellipsoid("Thin raised scoop",(.68,0,.16),(.27,.16,.048),"hinoki")
  ellipsoid("Scooped hollow",(.70,-.025,.205),(.22,.12,.016),"bamboo")
  for j in range(6):
   x=-.5+j*.18;rod("wood grain", (x,-.041,.16),(x+.08,-.041,.16),.006,"wooddark",6)
 elif i==3: # natsume lacquer
  revolve("Natsume black lacquer canister",[(.18,.04),(.40,.045),(.49,.16),(.54,.50),(.52,.80),(.42,.95),(.35,1.0)],"lacquer")
  cyl("Precisely fitting removable red lid",(0,0,.986),.425,.105,"red",36)
  hoop("Gold lid piping",(0,0,1.05),.413,.019,"gold")
  petals("Gold makie chrysanthemum",0, .56,.11,"gold",7,y=-.535)
  for z in (.15,.77):hoop("Gold linear accent",(0,0,z),.48 if z<.4 else .526,.012,"gold")
 elif i==4: # iron kettle
  revolve("Iron sand texture kettle",[(.2,.10),(.43,.11),(.59,.24),(.66,.48),(.62,.75),(.49,.91),(.29,.95)],"iron")
  cyl("Heavy iron lid",(0,0,.956),.34,.08,"iron",36)
  ellipsoid("Solid bronze finial",(0,0,1.04),(.11,.11,.09),"bronze")
  strand("Overarching heavy cast handle",[(-.57,0,.68),(-.69,0,1.05),(-.52,0,1.40),(0,0,1.58),(.52,0,1.40),(.69,0,1.05),(.57,0,.68)],"black",.07,12)
  rod("Angled pouring lip",(-.54,0,.72),(-.95,0,1.02),.10,"iron",16)
  ringdots("Hammered shoulder bumps",32,.625,.55,"charcoal",.03)
 elif i==5: # kyusu teapot
  revolve("Rounded hand-thrown kyusu",[(.20,.07),(.42,.10),(.59,.26),(.61,.55),(.52,.82),(.31,.87)],"clay")
  cyl("Tight ceramic lid",(0,0,.86),.34,.07,"celadon",32)
  ellipsoid("Lid button",(0,0,.945),(.105,.105,.085),"clay")
  rod("Side handle",(.48,0,.51),(1.01,0,.50),.115,"clay",16)
  hoop("Handle collar",(1.02,0,.50),.12,.027,"cream",20,"X")
  rod("Curved pouring spout",(-.49,0,.56),(-.87,0,.80),.11,"clay",16)
  hoop("Spout end",(-.90,0,.82),.10,.022,"cream",20,"X")
  for z in (.28,.34):hoop("Coiling line",(0,0,z),.596,.009,"cream")
 elif i==6: # tea cauldron
  revolve("Dome shaped tea cauldron",[(.2,.1),(.51,.14),(.69,.37),(.72,.69),(.56,.92),(.28,.99)],"iron",40)
  cyl("Inset tea-iron lid",(0,0,1.00),.34,.07,"black",36)
  ellipsoid("Gold sculpted lid boss",(0,0,1.105),(.09,.09,.08),"bronze")
  legs("Cast tripodal support",.45,.035,.2,3,"black")
  for s in (-1,1):
   hoop("Cast handle lug",(s*.67,0,.64),.14,.037,"bronze",24,"Y")
  ringdots("Hammered iron dots",24,.68,.51,"charcoal")
 elif i==7:
  revolve("Celadon water jar",[(.28,.03),(.53,.09),(.61,.27),(.60,.83),(.49,1.04),(.41,1.06)],"celadon",40)
  cyl("Flat hinoki lid",(0,0,1.09),.53,.10,"hinoki",32)
  hoop("Lid edge",(0,0,1.137),.49,.02,"wooddark")
  for z in (.18,.27,.36,.47):hoop("Raised glaze ring",(0,0,z),.59,.010,"cream")
  petals("Stamped porcelain medallion",0,.70,.13,"ivory",5,y=-.61)
 elif i==8:
  revolve("Bamboo scoop cup",[(.25,.04),(.30,.05),(.31,.46),(.29,.49),(.26,.47),(.25,.11),(.06,.1)],"bamboo")
  hoop("Thick exposed bamboo lip",(0,0,.475),.289,.028,"hinoki")
  rod("Long bamboo handle",(.16,0,.33),(1.42,0,.56),.055,"bamboo",16)
  for x in (.53,.88,1.18):
   ellipsoid("Growth node",(x,0,.35+.162*x),(.031,.064,.063),"bamboodark")
 elif i==9:
  revolve("Ceramic futaoki with recessed center",[(.20,.02),(.38,.05),(.43,.11),(.42,.45),(.35,.49),(.25,.44),(.26,.12)],"celadon")
  for z in (.17,.25,.33,.41):hoop("Hand-cut concentric ribs",(0,0,z),.425,.016,"clay")
  radial("Lid rest decorative radial carving",22,.13,.28,.49,"cream")
