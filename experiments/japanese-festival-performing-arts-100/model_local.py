"""Region-specific festival equipment, all miniature one-piece scenes."""
import math
from geometry import *
from parts import *
def make(i):
 if i==0:
  mask("Namahage fearful northern oni mask",5,"red")
  for s in (-1,1):
   rod("Long namahage horns",(s*.27,-.10,1.59),(s*.51,-.07,2.15),.12,"ivory",16,0)
   for j in range(5):
    a=T*j/5
    strand("Wild namahage straw mane",[(s*.42,0,1.15),(.55*s+.19*math.cos(a),0,1.5+.25*math.sin(a))],"straw",.058)
 elif i==1:
  polygon("Blunt wooden theatrical namahage knife blade",[(0,0,.90),(.90,0,1.13),(1.04,0,1.38),(.97,0,1.61),(0,0,1.43)],"steel",.073)
  rod("Stage-safe carved wood dagger grip",(-.75,0,1.10),(.07,0,1.12),.11,"cedar")
  box("Brass handle guard",(.02,0,1.12),(.12,.29,.32),"bronze")
  for x in (-.54,-.31):hoop("Wooden hilt brass binding",(x,0,1.11),.12,.017,"gold",16,"X")
 elif i==2:
  mask("Rare regional dekonnbo stylized mask",style=3,color="red")
  for s in (-1,1):
   strand("Hand-tied festival straw crest",[(s*.36,-.04,1.48),(s*.60,-.03,1.77),(s*.70,-.04,1.96)],"straw",.062)
  ellipsoid("Broad angular mouthpiece",(0,-.46,.74),(.35,.12,.18),"gold")
 elif i==3:
  ellipsoid("Festival kabuto decorated helmet",(0,0,.87),(.63,.49,.57),"iron",3)
  for s in (-1,1):
   polygon("Gold raised horn profile",[(s*.22,0,1.27),(s*.46,0,1.66),
      (s*.69,0,1.92),(s*.54,0,1.56)],"gold",.11)
   for j in range(5):
    z=.42+j*.13
    hoop("Helmet neckguard layers",(0,0,z),.66+.02*(4-j),.033,"lacquer",32)
  flower("Front chrysanthemum crest",(0,-.48,1.30),.16,"gold")
  box("Display sword stand",(0,0,.08),(1.63,1.02,.15),"wooddark")
 elif i==4:
  fan("Awa-odori bright festival bamboo fan",34,"red")
  flower("Festival printed indigo blossom",(0,-.06,1.13),.12,"indigo",8)
 elif i==5:
  revolve("Awa-odori tall pointed amigasa",[(.1,.38),(.45,.54),(.75,.93),(.55,1.33),(.05,1.63)],"straw",32)
  for j in range(36):
   a=T*j/36
   strand("Amigasa radial reeds",[(0,0,1.63),(.75*math.cos(a),.75*math.sin(a),.93)],"hinoki",.018)
  for z,r in [( .84,.68),(1.02,.68),(1.2,.6)]:
   hoop("Dense woven concentric brim",(0,0,z),r,.020,"bamboo",36)
  strand("Awa-odori chin strap",[(-.31,0,.72),(-.21,0,.36),(.21,0,.36),(.31,0,.72)],"red",.024)
 elif i==6:
  drum("Eisa paranku handheld drum",(0,0,.96),.47,.14,"Y","red",False)
  rod("Single-head paranku stick",(-.82,-.14,.09),(-.75,-.14,1.24),.05,"hinoki")
  flower("Okinawan red paranku mon",(0,-.10,.96),.17,"gold")
 elif i==7:
  drum("Large traditional Eisa Okinawa barrel",(0,0,1.06),.72,1.16,"Y","red",True)
  for s in (-1,1):
   strand("Eisa tied cross shoulder carrying strap",[(s*.52,-.38,.76),(s*.66,0,1.73),(s*.52,.38,.76)],"washi",.056)
  flower("Large Eisa drum face emblem",(0,-.62,1.07),.23,"gold")
 elif i==8:
  revolve("Tall kasaodori straw dance hat",[(.06,.48),(.49,.56),(1.06,.78),(.83,1.03),(.27,1.45)],"straw",36)
  for j in range(35):
   a=T*j/35
   rod("Kasaodori radial bamboo rib",(0,0,1.45),(1.04*math.cos(a),1.04*math.sin(a),.78),.018,"cedar")
  for j in range(18):
   a=T*j/18
   strand("Umbrella dancers red cloth strips",[(.86*math.cos(a),.86*math.sin(a),.88),
     (1.09*math.cos(a),1.09*math.sin(a),.56)],"red",.025)
 elif i==9:
  rod("Dengaku hoe carved wooden handle",(-.12,0,.07),(.08,0,1.9),.073,"cedar",18)
  polygon("Lightweight festival ritual hoe prop",[(-.46,0,1.58),(.49,0,1.58),(.59,0,1.90),(-.47,0,1.91)],"wooddark",.10)
  for j in range(15):
   x=-.44+j*.067
   strand("Dengaku ceremonial binding",[(x,-.06,1.63),(x,-.06,1.89)],"gold",.008)
  flower("Dengaku carved tool maker emblem",(0,-.08,1.77),.11,"red")
