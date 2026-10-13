import math
from geometry import *
def make(i):
 if i==0:
  box("Tansu wooden cabinet",(0,0,.71),(1.25,.65,1.42),"wood")
  for j in range(4):
   z=.26+j*.32;box("Drawer front",(0,-.344,z),(1.10,.04,.27),"wood2")
   ring("Drawer hardware",(0,-.37,z),.062,.015,"iron",10,"X")
  for x in (-.57,.57):box("Iron corner hardware",(x,-.35,1.35),(.08,.03,.12),"iron")
 elif i==1:
  cyl("Chabudai tabletop",(0,0,.64),.88,.15,"wood2",16)
  for x in (-.50,.50):
   for y in (-.50,.50):box("Short table leg",(x,y,.30),(.14,.14,.59),"wood")
 elif i==2:
  box("Zaisu seat",(0,0,.18),(1.06,1.01,.20),"wood")
  box("Zaisu backrest",(0,.42,.82),(1.06,.16,1.24),"wood2")
  box("Zaisu cloth cushion",(0,-.08,.31),(.92,.79,.12),"red")
 elif i==3:
  box("Kotatsu top",(0,0,.84),(1.46,1.14,.14),"wood2")
  box("Kotatsu quilt",(0,0,.46),(1.55,1.30,.70),"red")
  for x in (-.49,.49):
   for y in (-.36,.36):box("Kotatsu short leg",(x,y,.13),(.14,.14,.26),"wood")
 elif i==4:
  box("Nagamochi storage chest",(0,0,.48),(1.75,.77,.81),"wood")
  box("Nagamochi lid",(0,0,.94),(1.83,.86,.11),"wood2")
  for x in (-.80,.80):
   ring("Iron carrying handle",(x,0,.48),.15,.023,"iron",12,"X")
   box("Iron strap",(x,-.40,.49),(.07,.04,.80),"iron")
 elif i==5:
  box("Tsuitate standing screen",(0,0,1.01),(1.60,.09,1.66),"paper")
  for x in (-.85,.85):box("Screen pillar",(x,0,1),(.08,.17,1.95),"wood")
  for z in (.14,1.85):box("Screen frame",(0,0,z),(1.76,.18,.07),"wood2")
  for x in (-.60,.60):box("Screen footing",(x,0,.08),(.24,.78,.10),"wood")
 elif i==6:
  for z in (.16,.70,1.24,1.78):box("Book shelf",(0,0,z),(1.47,.47,.12),"wood2")
  for x in (-.69,.69):box("Shelf support",(x,0,.91),(.09,.46,1.82),"wood")
  for j in range(7):box("Bound volume",(-.55+j*.17,-.06,.40),(.11,.27,.40),["red","indigo","paper"][j%3])
 elif i==7:
  box("Fumikiri low step",(0,0,.62),(.94,.57,.15),"wood2")
  for x in (-.33,.33):box("Step riser",(x,0,.30),(.12,.57,.59),"wood")
  rod("Brace",(-.33,-.18,.35),(.33,-.18,.35),.04,"iron")
 elif i==8:
  cyl("Round wooden tray",(0,0,.12),.79,.20,"wood2",20)
  ring("Tray standing lip",(0,0,.20),.77,.045,"wood")
  orb("Carved center",(0,0,.23),(.23,.23,.025),"gold")
 else:
  box("Kumiko outer frame",(0,0,.76),(1.58,.11,1.5),"wood")
  box("Kumiko white backing",(0,-.062,.77),(1.42,.02,1.34),"paper")
  for j in range(9):
   x=-.66+j*.165;rod("Kumiko lattice",(x,-.09,.12),(x,-.09,1.4),.018,"wood2",6)
  for j in range(8):
   z=.19+j*.16;rod("Kumiko slat",(-.73,-.09,z),(.73,-.09,z),.018,"wood2",6)
