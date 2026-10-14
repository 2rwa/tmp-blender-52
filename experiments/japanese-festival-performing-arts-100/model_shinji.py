"""Sacred kagura and Shinto ceremony items with specific details."""
import math
from geometry import *
from parts import *
def make(i):
 if i in (0,2):
  pole("Ritual gohei wooden shaft",1.85,"hinoki")
  if i==0:
   for s in (-1,1):
    for k in range(6):
     z=.70+.18*k
     polygon("Gohei sharp zigzag white paper",[(s*.03,0,z),(s*.47,0,z+.16),
       (s*.47,0,z-.07),(s*.64,0,z-.07),(s*.64,0,z-.22),(s*.12,0,z-.22)],"washi",.019)
  else:
   for j in range(42):
    a=T*j/42
    strand("Haraegushi white purification fibre",[(0,0,1.83),(.10*math.cos(a),.10*math.sin(a),1.40),
        (.26*math.cos(a),.26*math.sin(a),.73)],"washi",.015)
 elif i==1:
  pole("Kagura bell ceremony staff",1.4,"cedar")
  for tier,z,r,n in [(0,.73,.36,7),(1,1.05,.30,6),(2,1.35,.21,5)]:
   for j in range(n):
    a=T*j/n;x,y=r*math.cos(a),r*math.sin(a)
    rod("Three-tiered kagura bell wire",(0,0,z-.22),(x,y,z),.021,"bronze")
    ellipsoid("Cast individual kagura bell",(x,y,z),(.10,.10,.10),"gold")
    hoop("Bell mouth",(x,y,z-.09),.065,.016,"iron")
 elif i==3:
  revolve("Raised tapered court eboshi hat",[(.30,.04),(.39,.11),(.43,.37),(.36,.93),(.17,1.45)],"black",24)
  for j in range(16):
   a=T*j/16
   strand("Eboshi lacquer fabric seam",[(.36*math.cos(a),.36*math.sin(a),.21),
       (.28*math.cos(a),.28*math.sin(a),1.09)],"charcoal",.017)
  strand("Rear narrow hat cord",[(-.33,0,.19),(-.42,0,.04),(.42,0,.04),(.33,0,.19)],"gold",.021)
 elif i==4:
  polygon("Carved ritual shaku rounded ivory staff",[(-.12,0,.06),(.12,0,.06),(.19,0,1.53),
     (.14,0,1.69),(-.14,0,1.69),(-.19,0,1.53)],"ivory",.073)
  for k in range(14):
   z=.20+k*.10
   rod("Shaku fine vertical wood grain",(-.14, -.04,z),(.14,-.04,z),.007,"hinoki")
 elif i==5:
  box("Raised houbei offering lacquer tray",(0,0,.4),(1.45,1.02,.13),"lacquer",.05)
  for s in (-1,1):
   box("Four legs below offering tray",(s*.54,s*.34,.18),(.11,.10,.36),"cedar")
  for x in (-.62,.62):box("Gilt rim",(x,0,.47),(.035,1.04,.06),"gold")
  flower("Houbei gold crest",(0,-.40,.50),.12)
 elif i==6:
  box("Sanbo square wooden tray",(0,0,1.07),(1.32,1.10,.17),"hinoki",.05)
  box("Hollow sanbo pedestal",(0,0,.53),(.70,.58,.97),"cedar",.07)
  for y in (-.30,.30):box("Carved sanbo opening",(0,y,.61),(.39,.03,.35),"black",.005)
  for x in (-.37,.37):box("Sanbo outer joinery",(x,0,.55),(.048,.63,.95),"hinoki")
 elif i==7:
  drum("Sacred fixed shinto shrine drum",(0,0,1.04),.67,.52,"Y","red",True)
  for s in (-1,1):
   rod("Drum stand arch foot",(s*.66,-.32,.05),(s*.54,-.3,.92),.08,"cedar")
  for x in (-.6,.6):rod("Crossbrace",(x,-.32,.11),(x,.32,.11),.06,"wooddark")
  flower("Shrine drum traditional mon",(0,-.29,1.04),.16,"gold")
 elif i==8:
  fan("Ceremonial kagura folding fan",34,"gold")
  for j in range(16):
   a=-.9+j*.12
   strand("White kagura decorative threads",[(.94*math.sin(a),0,.18+.94*math.cos(a)),
          (1.20*math.sin(a),0,.18+1.20*math.cos(a))],"red",.009)
 elif i==9:
  revolve("Sakaki display sake-green ceramic vase",[(.25,.03),(.44,.07),(.53,.52),(.30,.85),(.26,.94)],"jade")
  for j in range(24):
   a=T*j/24
   rod("Branching sakaki florist stem",(.10*math.cos(a),.10*math.sin(a),.77),
        (.62*math.cos(a),.62*math.sin(a),1.61),.026,"bamboodark")
   ellipsoid("Evergreen sacred foliage",(.55*math.cos(a),.55*math.sin(a),1.60),(.23,.09,.14),"green",2)
  hoop("Sakaki vase mouth gold",(0,0,.94),.27,.03,"gold")
