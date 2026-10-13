import math
from geometry import *
from geometry_panel import fan
def face_eyes(z=.85,x=.19,y=-.48):
 for s in (-1,1):orb("Eye",(s*x,y,z),(.07,.035,.075),"black")
def make(i):
 if i==0:
  orb("Daruma crimson body",(0,0,.61),(.61,.47,.67),"red",2)
  orb("Daruma face",(0,-.43,.91),(.40,.09,.39),"paper")
  face_eyes(1,.19,-.53)
  for s in (-1,1):orb("Brow",(s*.18,-.56,1.17),(.16,.04,.045),"black")
  orb("Gold belly",(0,-.45,.48),(.27,.045,.18),"gold")
 elif i==1:
  cyl("Kokeshi body",(0,0,.51),.28,.88,"red")
  orb("Kokeshi wooden head",(0,0,1.13),(.39,.34,.38),"wood2",2)
  cyl("Kokeshi hair cap",(0,0,1.43),.34,.16,"black")
  face_eyes(1.12,.15,-.335)
  orb("Painted flower",(0,-.28,.58),(.15,.03,.15),"gold")
 elif i==2:
  orb("Lucky cat body",(0,0,.55),(.44,.36,.59),"white",2)
  orb("Lucky cat head",(0,-.04,1.12),(.48,.40,.41),"white",2)
  for s in (-1,1):orb("Pointed ear",(s*.33,0,1.50),(.17,.15,.21),"pink")
  face_eyes(1.16,.18,-.43)
  orb("Collar bell",(0,-.38,.75),(.10,.07,.10),"gold")
  rod("Raised lucky paw",(.38,-.07,.59),(.51,-.08,1.37),.16,"white")
 elif i==3:
  rod("Kendama handle",(0,0,.1),(0,0,1.11),.095,"wood")
  rod("Kendama horizontal cups",(-.53,0,.7),(.53,0,.7),.11,"wood2")
  for s in (-1,1):cyl("Catch cup",(s*.48,0,.76),.23,.10,"wood2")
  orb("Kendama red ball",(.57,0,.24),(.24,.24,.24),"red",2)
  rod("String",(0,0,.92),(.57,0,.24),.012,"white")
 elif i==4:
  cyl("Koma upper top",(0,0,.34),.54,.43,"red",16,0)
  cyl("Koma lower cone",(0,0,.13),.49,.22,"wood2",16,0)
  rod("Spinning spindle",(0,0,.0),(0,0,.85),.062,"wood")
  ring("Colored top band",(0,0,.54),.24,.04,"gold")
 elif i==5:
  box("Hagoita paddle",(0,0,1.06),(.63,.10,1.05),"wood2")
  rod("Hagoita handle",(0,0,.03),(0,0,.56),.10,"wood")
  fan("Hagoita ornament",.82,.41,8,"red")
  orb("Lacquer flower",(0,-.08,1.35),(.16,.04,.17),"gold")
 elif i==6:
  for j in range(3):
   x=(j-1)*.47;orb("Otedama beanbag",(x,0,.22+(.16 if j==1 else 0)),(.28,.26,.23),["red","blue","gold"][j],2)
 elif i==7:
  cyl("Denden daiko drum",(0,0,.91),.43,.23,"red",16).rotation_euler[0]=math.pi/2
  rod("Drum stick",(0,0,.12),(0,0,.80),.07,"wood")
  for s in (-1,1):
   rod("Beat string",(s*.28,0,.90),(s*.74,0,.84),.013,"white")
   orb("Percussion bead",(s*.75,0,.84),(.10,.10,.10),"gold")
 elif i==8:
  orb("Akabeko body",(0,0,.52),(.71,.34,.38),"red",2)
  orb("Akabeko head",(-.53,-.04,.98),(.32,.29,.34),"red")
  for x in (-.45,.42):
   for y in (-.18,.18):cyl("Akabeko leg",(x,y,.20),.09,.36,"red")
  for s in (-1,1):cyl("White cow horn",(-.64,s*.21,1.24),.08,.22,"white",8,0)
  orb("Cow eye",(-.66,-.30,1.04),(.06,.03,.06),"white")
 else:
  orb("Hariko tiger torso",(0,0,.54),(.72,.30,.38),"orange",2)
  orb("Tiger head",(-.60,0,.89),(.29,.26,.30),"orange")
  for x in (-.44,.45):
   for y in (-.19,.19):cyl("Tiger foot",(x,y,.22),.10,.37,"orange")
  for x in (-.45,-.15,.15,.45):box("Painted tiger stripe",(x,-.295,.76),(.075,.03,.33),"black")
  rod("Curved tiger tail",(.60,0,.78),(.9,0,1.22),.065,"black")
