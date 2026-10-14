"""Dance accessories, lion head, fox and oni masks, wooden binzasara."""
import math
from geometry import *
from parts import *
def make(i):
 if i in (0,4):
  fan("Nihon buyo silk folding fan",32 if i==0 else 42,"gold" if i==0 else "red")
  if i==4:
   for j in range(12):
    a=-1+j*.18
    flower("Mai ogi ornate woven pattern",(.9*math.sin(a),-.06,.18+.9*math.cos(a)),.06,"ivory")
 elif i==1:
  pole("Hand dance ringing bell shaft",1.19,"cedar",0,0,.05)
  for j in range(15):
   a=T*j/15
   x=.35*math.cos(a);y=.35*math.sin(a)
   strand("Dance bell hanging wire",[(0,0,.97),(x,y,1.13)],"gold",.015)
   ellipsoid("Suzu individual ceremonial bell",(x,y,1.13),(.099,.093,.09),"gold")
  fringe("Ceremonial hand bell tassels",0,-.06,.44,.37,12,"red")
 elif i==2:
  pole("Decorated dance umbrella shaft",2.2,"cedar")
  for j in range(32):
   a=j*T/32
   polygon("Dance umbrella thick washi canopy",[(0,0,1.95),(.48*math.cos(a),.48*math.sin(a),1.90),
      (1.01*math.cos(a),1.01*math.sin(a),1.47),
      (1.01*math.cos(a+T/32),1.01*math.sin(a+T/32),1.47)],
      "red" if j%3 else "gold",.02)
   rod("Bamboo canopy rib",(0,0,1.94),(1.01*math.cos(a),1.01*math.sin(a),1.47),.023,"hinoki")
  for j in range(22):
   a=j*T/22
   strand("Dance umbrella dangling silk tassel",[(.98*math.cos(a),.98*math.sin(a),1.47),
       (1.0*math.cos(a),1.0*math.sin(a),1.17)],"gold",.013)
 elif i==3:
  textile("Woven tenugui stage cloth",(0,0,.89),(1.38,.052,1.63),"washi",29)
  for j in range(15):
   x=-.62+j*.085
   rod("Repeating blue tenugui pattern",(x,-.035,.26),(x,-.035,1.44),.025,"indigo",6)
  for z in (.18,1.52):
   rod("Red sewn textile hem",(-.66,-.03,z),(.66,-.03,z),.016,"red")
 elif i==5:
  ellipsoid("Shishimai deep carved red skull",(0,0,1.05),(.56,.43,.62),"red",3)
  ellipsoid("Lion wide hinged lower jaw",(0,-.33,.53),(.48,.21,.23),"red",3)
  for s in (-1,1):
   ellipsoid("Exaggerated lion painted round eye",(s*.26,-.39,1.20),(.16,.09,.16),"gold")
   ellipsoid("Black pupils",(s*.26,-.475,1.21),(.057,.016,.065),"black")
   ellipsoid("Lion curled side ear",(s*.51,0,1.21),(.21,.19,.18),"gold")
   rod("Lion prominent ivory fang",(s*.29,-.48,.69),(s*.29,-.48,.41),.056,"ivory",12,0)
  ellipsoid("Massive painted lion snout",(0,-.52,.90),(.27,.17,.18),"gold")
  for j in range(13):
   a=j*T/13
   strand("Wild cream lion mane",[(.4*math.cos(a),.11,.9+.37*math.sin(a)),
     (.67*math.cos(a),.16,.9+.52*math.sin(a))],"ivory",.052)
  for k in range(12):
   x=-.36+k*.065
   ellipsoid("Visible ivory lion teeth",(x,-.53,.62),(.027,.029,.066),"ivory",1)
 elif i==6:
  costume("Shishimai cotton green striped dance cloth","green","gold")
  for j in range(17):
   x=-.82+j*.10
   for k in range(8):
    z=.24+k*.18
    ellipsoid("Indigo shishimai scale pattern",(x,-.18,z),(.05,.016,.047),"indigo")
 elif i in (7,8):
  mask("Folk festival carved fox or oni mask",style=4 if i==7 else 5,
       color="ivory" if i==7 else "red")
  if i==7:
   for s in (-1,1):
    strand("Kitsune elongated painted cheek",[ (s*.12,-.48,1.23),(s*.36,-.40,1.13),
       (s*.48,-.28,.83)],"red",.026)
  else:
   ellipsoid("Brutal oni wide brow",(0,-.36,1.43),(.40,.12,.11),"black")
 elif i==9:
  for j in range(36):
   x=-.77+j*.044
   box("Thirty-six individual binzasara wooden slat",(x,0,.74),(.036,.28,1.28),"hinoki",.005)
   for z in (.22,.51,.95,1.23):
    ellipsoid("Wooden slat carved joinery",(x,-.16,z),(.014,.013,.03),"red",1)
  for z in (.17,1.35):rod("Actual silk binzasara connecting cord",(-.82,0,z),(.82,0,z),.022,"red")
