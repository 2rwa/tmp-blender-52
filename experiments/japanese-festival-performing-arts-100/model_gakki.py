"""10 separately identifiable wa-gakki with real fittings, skins and reeds."""
import math
from geometry import *
from parts import *
def make(i):
 if i==0:
  drum("Nagado full taiko",(0,0,.95),.67,.86,"Y","red",False)
  for s in (-1,1):
   rod("Angled nagado taiko stand",(s*.67,-.27,.05),(s*.43,-.27,.74),.084,"cedar")
   rod("Cross bracing",(s*.60,.28,.08),(s*.43,-.27,.65),.055,"wooddark")
  for s in (-1,1):rod("Taiko hand bachi",(s*.82,-.42,.14),(s*.70,-.42,1.22),.041,"hinoki",16)
 elif i==1:
  drum("Shime-daiko taut double-headed",(0,0,.86),.56,.32,"Y","cedar",True)
  for j in range(24):
   a=T*j/24
   strand("Red cord crossed lacing",[(.55*math.cos(a),-.22,.86+.55*math.sin(a)),
       (.53*math.cos(a+.24),0,.86+.53*math.sin(a+.24)),(.55*math.cos(a+.48),.22,.86+.55*math.sin(a+.48))],"red",.026)
  for s in (-1,1):box("Lacquered shime daiko stand",(s*.45,0,.28),(.07,.46,.53),"wooddark")
 elif i==2:
  drum("Okedo cylindrical long stave drum",(0,0,.89),.62,1.15,"Y","hinoki",True)
  for j in range(36):
   a=T*j/36
   rod("Wooden okedo staves",(.62*math.cos(a),-.50,.89+.62*math.sin(a)),
      (.62*math.cos(a),.50,.89+.62*math.sin(a)),.014,"cedar")
  for s in (-1,1):hoop("Okedo decorative rim",(0,s*.57,.89),.65,.06,"red",36,"Y")
 elif i==3:
  drum("Uchiwa drum thin painted frame",(0,0,1.26),.51,.07,"Y","red",False)
  rod("Uchiwa drum long bamboo shaft",(0,0,.02),(0,0,.97),.060,"cedar",18)
  flower("Painted Nichiren lotus",(0,-.073,1.26),.17,"gold")
  for j in range(9):
   a=T*j/9
   rod("Drum raised rays",(0,-.065,1.26),(.43*math.cos(a),-.065,1.26+.43*math.sin(a)),.012,"gold")
 elif i in (4,5):
  revolve("Hand cast atarigane gong",[(.21,.12),(.46,.14),(.51,.26),(.53,.34),(.49,.40),(.44,.30),(.20,.28)],"bronze",36)
  hoop("Bell forge rim",(0,0,.35),.53,.04,"gold")
  for j in range(24):
   a=T*j/24
   ellipsoid("Gong ring tooling",(.42*math.cos(a),.42*math.sin(a),.34),(.025,.025,.015),"iron",1)
  rod("Fine metal gong clapper",(.70,0,.03),(.84,0,1.20),.055,"cedar")
  ellipsoid("Gong mallet padded striking head",(.84,0,1.24),(.14,.12,.17),"ivory")
  if i==5:
   for s in (-1,1):rod("Added crossed wooden kane-bachi",(s*.82,-.25,.08),(s*.55,-.28,.91),.04,"hinoki")
 elif i in (6,7):
  rod("Bamboo horizontal shinobue or ryuteki",(-1.23,0,.19),(1.23,0,.19),.083,"bamboo" if i==6 else "wooddark",22)
  for j in range(8):
   x=-.76+j*.18
   ellipsoid("Finger hole", (x,-.084,.20),(.044,.011,.040),"black")
  for k in range(15):
   x=-1.1+k*.15
   if i==7 or k in (0,2,9,12,14):
    hoop("Fine red transverse silk binding",(x,0,.19),.085,.013,"red",20,"X")
  ellipsoid("Flute embouchure",(-1.01,-.086,.19),(.06,.01,.037),"black")
 elif i==8:
  ellipsoid("Horagai spiral giant shell body",(0,0,.63),(.72,.37,.49),"ivory",3)
  for j in range(9):
   x=-.56+j*.15
   hoop("Concentric trumpet spiral ridge",(x,0,.66),.32+.04*math.sin(j),.02,"bronze",24,"X")
  for j in range(8):
   a=T*j/8
   ellipsoid("Natural scalloped shell lip",( .57,.30*math.cos(a),.66+.30*math.sin(a)),(.10,.06,.06),"ivory")
  rod("Horagai copper sound mouthpiece",(-.66,0,.70),(-1.03,0,.80),.09,"bronze",16)
  strand("Horagai braided carrying cord",[(-.68,-.20,.95),(0,-.32,1.42),(.56,-.18,.98)],"red",.035)
 elif i==9:
  for j in range(35):
   x=-.64+j*.038
   box("Sliding fine wood sasara slat",(x,0,.73),(.025,.28,1.19),"hinoki",.004)
   for z in (.27,1.17):rod("Sasara binding silk rope",(-.72,-.15,z),(.72,-.15,z),.014,"red")
  for s in (-1,1):box("Sasara terminating paddle",(s*.73,0,.70),(.12,.34,1.31),"cedar")
