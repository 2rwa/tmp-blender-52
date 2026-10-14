"""Festival uniform, shoes, silk bands, miko robes and yamabushi gear."""
import math
from geometry import *
from parts import *
def make(i):
 if i==0:
  costume("Traditional matsuri happi coat","indigo","washi")
  for x in (-.14,.14):
   strand("Happi vertically woven white collar",[(x,-.17,1.52),(x,-.19,1.02),(x,-.18,.30)],"washi",.046)
  flower("Large rear happi crest",(0,.14,1.12),.21,"washi")
 elif i==1:
  for j in range(12):
   a=T*j/12
   strand("Twisted cotton hachimaki band",[(.43*math.cos(a),.43*math.sin(a),.92),
      (.43*math.cos(a),.43*math.sin(a),1.16)],"washi",.04)
  for j in range(7):
   x=-.14+j*.04
   strand("Double tied headband tails",[(x,-.43,1.0),(x,-.52,.66),(x+.03,-.51,.28)],"washi",.02)
  hoop("Rounded ceremonial wearer headband",(0,0,1.05),.45,.08,"red")
 elif i==2:
  for s in (-1,1):
   x=s*.34
   ellipsoid("Split-toe tabi rising ankle",(x,.19,.52),(.23,.23,.48),"ivory",3)
   ellipsoid("Stitched soft shoe foot",(x,-.20,.18),(.30,.44,.18),"washi",3)
   ellipsoid("Tabi independently split big toe",(x-.11,-.51,.12),(.12,.20,.12),"ivory")
   ellipsoid("Tabi other toe section",(x+.12,-.50,.12),(.16,.18,.12),"washi")
   for j in range(7):
    ellipsoid("Tiny tabi side fastening button",(x+.21,.37,.19+j*.10),(.020,.014,.025),"black",1)
 elif i==3:
  for s in (-1,1):
   x=s*.38
   ellipsoid("Straw waraji shoe sole",(x,0,.10),(.31,.58,.13),"straw",3)
   for j in range(19):
    y=-.49+j*.053
    rod("Individual rice-straw woven strand",(x-.23,y,.19),(x+.23,y,.19),.014,"hinoki",8)
   for k in (-1,1):
    strand("Woven waraji ankle tie",[(x+k*.25,.18,.16),(x+k*.34,.40,.48),(x,.46,.69)],"straw",.031)
 elif i==4:
  for s in (-1,1):
   x=.37*s
   box("Traditional festival geta sandal wooden sole",(x,0,.47),(.54,1.03,.13),"hinoki",.052)
   for y in (-.30,.29):box("Carved geta heel tooth",(x,y,.23),(.48,.17,.39),"cedar")
   strand("Thick vermilion hanao strap",[(x-.20,-.22,.53),(x, .20,.78),(x+.21,-.22,.53)],"red",.05)
   for j in range(8):
    y=-.42+j*.12
    rod("Geta grain",(x-.23,y,.56),(x+.23,y,.56),.012,"cedar")
 elif i==5:
  for s in (-1,1):
   cyl("Ritual leg strap lower clasp",(s*.39,0,.26),.31,.18,"indigo",20)
   for j in range(16):
    a=T*j/16
    ellipsoid("Jingling suzu attached to anklet",(s*.39+.31*math.cos(a),.31*math.sin(a),.27),(.09,.09,.087),"gold",2)
   for z in (.19,.33):hoop("Woven leg binding",(s*.39,0,z),.31,.031,"red")
 elif i==6:
  costume("Miko long-sleeve white chihaya","washi","red")
  for s in (-1,1):
   for j in range(6):
    z=.30+j*.16
    ellipsoid("Crimson miko embroidery",(s*.72,-.13,z),(.048,.021,.074),"red")
  strand("Miko decorative neck cord",[(-.2,-.14,1.55),(0,-.23,1.2),(.2,-.14,1.55)],"gold",.019)
 elif i==7:
  box("Miko crimson pleated hakama",(0,0,.55),(.92,.38,1.04),"red",.06)
  for k in range(20):
   x=-.45+k*.046
   rod("Individually modeled hakama pleat",(x,-.198,.09),(x,-.198,1.06),.018,"vermilion",8)
  box("Wide traditional folded obi",(0,-.18,1.11),(1.03,.13,.21),"washi")
  for s in (-1,1):fringe("Crimson hakama hem",s*.25,-.12,.07,.38,10,"red")
 elif i==8:
  revolve("Black yamabushi tokin headpiece",[(.27,.08),(.39,.19),(.46,.48),(.44,.66),(.38,.72)],"black",16)
  for j in range(10):
   a=T*j/10
   box("Tokin folded lacquer facets",(.41*math.cos(a),.41*math.sin(a),.5),(.09,.06,.37),"charcoal",.008)
  strand("Tokin textile binding",[(-.40,0,.14),(-.48,0,.08),(0,-.58,.03),(.48,0,.08),(.40,0,.14)],"red",.025)
 elif i==9:
  ellipsoid("Yamabushi horagai heavy shell",(0,0,.70),(.66,.40,.39),"ivory",3)
  for j in range(8):
   x=-.5+j*.15
   hoop("Concentric natural seashell coils",(x,0,.73),.27+.03*j,.017,"bronze",20,"X")
  strand("Ceremonial cloth shoulder strap",[(-.58,0,.74),(-.55,0,1.18),(-.18,0,1.55),(.22,0,1.59),(.52,0,1.25),(.58,0,.74)],"red",.045)
  for k in range(9):
   x=-.4+k*.1
   rod("Horagai wooden fibers",(x,-.41,.42),(x,-.40,.84),.007,"cedar")
