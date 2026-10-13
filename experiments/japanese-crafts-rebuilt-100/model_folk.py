"""Traditional folk toys: distinct heads, painting, limbs, and mechanics."""
import math
from geometry import *
def eyes(name,x,z,y=-.48,color="black"):
 for s in (-1,1):ellipsoid(name+str(s),(s*x,y,z),(.055,.027,.07),color)
def make(i):
 if i==0:
  ellipsoid("Weighted Daruma red lacquer body",(0,0,.72),(.62,.54,.76),"red",3)
  ellipsoid("Daruma ivory face",(0,-.47,.99),(.42,.12,.43),"washi",3)
  eyes("Bold Daruma eyes",.20,1.07,-.583)
  for s in (-1,1):
   ellipsoid("Daruma eyebrow",(s*.21,-.58,1.31),(.17,.035,.055),"black")
   strand("Swirled cheek outline",[(s*.33,-.56,.94),(s*.27,-.58,.83),(s*.17,-.60,.79)],"gold",.021)
  ellipsoid("Belly central blessing badge",(0,-.53,.48),(.29,.047,.22),"gold")
  for z in (.17,.26):hoop("Underside painted circular trim",(0,0,z),.48,.024,"black")
 elif i==1:
  revolve("Artisan turned kokeshi wooden body",[(.16,.02),(.32,.08),(.36,.55),(.27,1.07),(.21,1.15)],"hinoki")
  ellipsoid("Hand-carved kokeshi head",(0,0,1.31),(.41,.39,.42),"hinoki",3)
  ellipsoid("Deep blue lacquered bangs",(0,-.01,1.60),(.40,.38,.18),"black")
  eyes("Kokeshi delicate black eyes",.15,1.36,-.39)
  for z in (.28,.44,.71):hoop("Vermilion robe painted ring",(0,0,z),.35 if z<.6 else .33,.028,"red")
  petals("Kokeshi flower on kimono",0,.60,.13,"red",6,y=-.348)
 elif i==2:
  ellipsoid("Manekineko white ceramic seated body",(0,0,.56),(.49,.41,.58),"ivory",3)
  ellipsoid("Manekineko round head",(0,-.05,1.18),(.47,.38,.42),"ivory",3)
  for s in (-1,1):
   polygon("Triangular cat ear",[(s*.21,-.05,1.42),(s*.40,-.04,1.69),(s*.47,-.05,1.40)],"pink",.10)
   ellipsoid("Happy closed eye",(s*.17,-.42,1.18),(.075,.02,.05),"black")
   strand("Cat painted whiskers",[(s*.15,-.44,1.04),(s*.46,-.43,1.02)],"charcoal",.012)
  ellipsoid("Raised beckoning front paw",(.47,-.25,.96),(.18,.17,.42),"ivory")
  ellipsoid("Gold fortune coin",(-.19,-.41,.49),(.18,.047,.23),"gold")
  hoop("Red collar",(0,-.05,.85),.40,.042,"red")
  ellipsoid("Collar bell",(0,-.46,.86),(.092,.06,.09),"gold")
 elif i==3:
  rod("Lathed kendama pine grip",(0,0,.10),(0,0,1.32),.083,"hinoki",20)
  rod("Kendama horizontal crossbeam",(-.56,0,.78),(.56,0,.78),.115,"cedar",20)
  for s in (-1,1):
   cup=revolve("Separate concave catch cup",[(.07,.02),(.22,.07),(.30,.14),(.27,.18),(.18,.16),(.06,.10)],"hinoki",24)
   cup.location=(s*.50,0,.82)
   hoop("Rim of wooden kendama cup",(s*.50,0,1.00),.27,.027,"cedar",20)
  ellipsoid("Red lacquer kendama ball",(.78,0,.36),(.26,.26,.26),"red",3)
  strand("Actual kendama tether",[(0,0,1.22),(.33,0,.73),(.60,0,.53),(.78,0,.36)],"ivory",.013)
  cyl("Sharpened spike",(0,0,1.33),.08,.36,"hinoki",20,0)
 elif i==4:
  cyl("Traditional spinning top striped upper",(0,0,.42),.53,.34,"red",32,top=.21)
  cyl("Pointed tapered lower cone",(0,0,.17),.49,.31,"hinoki",32,top=.02)
  for z,r in [(.30,.53),(.43,.51),(.56,.40)]:
   hoop("Lacquer top concentric stripe",(0,0,z),r,.032,"gold",32)
  rod("Turned pointed axle",(0,0,.03),(0,0,.91),.054,"cedar",18)
 elif i==5:
  polygon("Hagoita pear-shaped wooden head",[(-.33,0,.65),(-.44,0,.87),(-.42,0,1.58),(-.25,0,1.70),
     (.25,0,1.70),(.42,0,1.58),(.44,0,.87),(.33,0,.65)],"hinoki",.10)
  rod("Hagoita tapered grip",(0,0,.08),(0,0,.71),.10,"cedar",16)
  petals("Lacquer cherry blossom",-0.09,1.25,.18,"pink",7,y=-.065)
  ellipsoid("Gold symbolic cord",(.18,-.07,1.09),(.13,.022,.20),"gold")
  for j in range(6):strand("Hagoita painted accent",[( -.3+j*.12,-.06,.75),(-.32+j*.12,-.06,.95)],"red",.015)
 elif i==6:
  for j,(x,y,z) in enumerate([(-.42,0,.25),(.44,0,.24),(0,-.18,.60)]):
   ellipsoid("Otedama handmade patterned beanbag", (x,y,z),(.29,.25,.25),
             ["red","indigo","gold"][j],3)
   for k in range(8):
    a=k*math.tau/8
    rod("Otedama contrasting sewn seam",(x+.22*math.cos(a),y-.23,z+.15*math.sin(a)),
      (x+.22*math.cos(a+.12),y-.23,z+.15*math.sin(a+.12)),.014,"washi")
 elif i==7:
  cyl("Denden daiko miniature barrel",(0,0,.95),.47,.23,"cedar",32).rotation_euler.x=math.pi/2
  for y in (-.13,.13):hoop("Taut drum skin rim",(0,y,.95),.467,.036,"gold",36,"Y")
  cyl("Carved handle",(0,0,.36),.071,.77,"hinoki",20)
  for s in (-1,1):
   strand("Beater hanging string",[(s*.36,0,.99),(s*.60,0,.89),(s*.76,0,.92)],"washi",.019)
   ellipsoid("Lacquer rattle bead",(s*.76,0,.92),(.12,.11,.12),"red")
  petals("Painted drum emblem",0,.95,.12,"gold",7,y=-.15)
 elif i==8:
  ellipsoid("Akabeko papier-mache red body",(0,0,.62),(.77,.37,.42),"red",3)
  ellipsoid("Separate Akabeko head",(-.68,-.05,1.01),(.34,.33,.37),"red",3)
  for x in (-.53,.50):
   for y in (-.25,.25):rod("Akabeko sturdy foot",(x,y,.04),(x,y,.48),.105,"vermilion",12)
  for s in (-1,1):
   cyl("Akabeko curved cream horn",(-.75,s*.22,1.33),.074,.21,"ivory",12,0)
   ellipsoid("Cheek blossom",(-.79,s*.30,1.10),(.055,.025,.06),"ivory")
  ellipsoid("Akabeko painted eye",(-.86,-.32,1.12),(.065,.022,.055),"black")
  hoop("Nodding neck collar",(-.44,0,.85),.23,.032,"black",20,"X")
  for x in (-.22,.26):ellipsoid("Decorative saddle spot",(x,-.36,.82),(.18,.018,.10),"ivory")
 elif i==9:
  ellipsoid("Orange painted tiger torso",(0,0,.63),(.78,.39,.43),"orange",3)
  ellipsoid("Tiger distinct feline head",(-.67,-.03,1.06),(.34,.31,.32),"orange",3)
  for s in (-1,1):
   polygon("Tiger pointy ear",[(-.85,-.03,1.26),(-.77+s*.14,-.04,1.49),(-.60,-.03,1.29)],"black",.075)
  for x in (-.57,.55):
   for y in (-.26,.26):rod("Tiger four paws",(x,y,.04),(x,y,.48),.105,"orange")
  for x in (-.53,-.28,0,.29,.54):
   polygon("Distinct tiger black stripes",[(x-.045,-.39,.89),(x+.08,-.405,.81),(x+.14,-.39,.68)],"black",.032)
  strand("Long curved tiger tail",[(.68,0,.69),(.91,0,.90),(1.02,0,1.25),(.92,0,1.38)],"orange",.078)
  ellipsoid("Tiger face black nose",(-.94,-.31,1.0),(.06,.06,.045),"black")
