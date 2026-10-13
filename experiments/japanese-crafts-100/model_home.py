import math
from geometry import *
def make(i):
 if i==0:
  box("Andon rice paper",(0,0,.73),(.8,.67,1.2),"paper")
  for x in (-.41,.41):
   for y in (-.35,.35):box("Bamboo post",(x,y,.73),(.055,.055,1.46),"wood")
  for z in (.12,1.35):box("Frame",(0,0,z),(.91,.8,.07),"wood2")
 elif i==1:
  for j in range(9):cyl("Chochin lantern section",(0,0,.3+j*.13),.33+.16*math.sin(math.pi*(j+1)/10),.135,"red",18)
  for z in (.24,1.52):ring("Lantern cap",(0,0,z),.32,.03,"black")
  ring("Suspension",(0,0,1.63),.12,.027,"iron",12,"Y")
 elif i==2:
  orb("Bonbori white lamp",(0,0,.99),(.62,.62,.53),"paper",2)
  cyl("Lamp stand",(0,0,.38),.08,.7,"wood")
  cyl("Lamp foot",(0,0,.05),.43,.09,"wood2");ring("Lamp collar",(0,0,.59),.17,.04,"gold")
 elif i==3:
  box("Ceramic firebowl",(0,0,.35),(1.1,1.1,.7),"clay")
  box("Charcoal ash",(0,0,.71),(.95,.95,.03),"gray")
  for x in (-.3,.23):orb("Charcoal",(x,.1,.78),(.26,.17,.15),"black")
 elif i==4:
  for x in (-.70,.70):
   for y in (-.5,.5):rod("Mosquito net corner",(x,y,0),(x,y,1.6),.019,"white")
  box("Suspended kaya fabric",(0,0,1.60),(1.46,1.07,.08),"paper")
  for j in range(12):rod("Net strand",(-.70+j*.128,-.52,.03),(-.70+j*.128,-.52,1.6),.007,"white",6)
 elif i==5:
  rod("Noren rod",(-.97,0,1.59),(.97,0,1.59),.045,"wood")
  for j in range(3):box("Split noren cloth",(-.64+j*.64,0,1.04),(.59,.035,1.00),"indigo")
  for j in range(3):orb("White crest",(-.64+j*.64,-.04,1.15),(.12,.02,.12),"white")
 elif i==6:
  for j in range(4):
   box("Byobu folding panel",(-.77+j*.51,.08*(j%2),.75),(.49,.04,1.45),"gold")
   box("Byobu painted scene",(-.77+j*.51,-.03,.80),(.40,.024,1.18),"paper")
   box("Mountain ink",(-.77+j*.51,-.054,.66),(.22,.015,.24),"indigo")
 elif i==7:
  box("Tatami mat",(0,0,.075),(1.80,.95,.15),"bamboo")
  for y in (-.43,.43):box("Tatami edging",(0,y,.14),(1.82,.09,.02),"indigo")
  for j in range(15):box("Tatami straw line",(-.80+j*.11,0,.154),(.018,.78,.008),"bamboo2")
 elif i==8:
  box("Zabuton cushion",(0,0,.16),(1.23,1.23,.32),"red")
  for x,y in [(-.50,-.5),(.5,-.5),(-.5,.5),(.5,.5)]:orb("Corner tassel",(x,y,.12),(.085,.085,.08),"gold")
  orb("Center stitch",(0,0,.34),(.07,.07,.026),"gold")
 else:
  orb("Wind chime bell",(0,0,1.05),(.35,.35,.39),"blue",2)
  cyl("Wind chime lip",(0,0,.76),.32,.045,"gold");rod("Cord",(0,0,.80),(0,0,.25),.016,"black")
  box("Paper wind strip",(0,0,.20),(.24,.025,.36),"paper")
  ring("Hanging hook",(0,0,1.51),.10,.019,"gold",12,"Y")
