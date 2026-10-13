import math
from geometry import *
def make(i):
 if i==0:
  box("Ema votive tablet",(0,0,.79),(1.05,.11,1.10),"wood2")
  rod("Ema hanging cord",(0,0,1.34),(0,0,1.68),.022,"red")
  orb("Ema painted crest",(0,-.07,.88),(.24,.024,.21),"red")
 elif i==1:
  box("Omamori charm bag",(0,0,.66),(.69,.16,1.03),"red")
  ring("Omamori knot",(0,0,1.31),.13,.027,"gold",14,"Y")
  box("Gold charm seal",(0,-.093,.74),(.24,.016,.31),"gold")
 elif i==2:
  ring("Braided shimenawa rope",(0,0,.95),.69,.15,"bamboo",24,"Y")
  for x in (-.40,0,.40):
   box("White paper streamer",(x,-.04,.52),(.16,.026,.40),"white")
   box("Folded shide",(x+.11,-.04,.38),(.18,.026,.18),"white")
 elif i==3:
  rod("Kagura bell grip",(0,0,.16),(0,0,1.31),.08,"wood")
  for j in range(3):
   for k in range(5):
    a=k*math.tau/5;orb("Suzu bell",(.21*math.cos(a),.21*math.sin(a),.65+j*.22),(.11,.11,.11),"gold")
 elif i==4:
  box("Omikuji paper slip",(0,0,.65),(.26,.04,1.20),"paper")
  for j in range(9):box("Fortune black ink",(0,-.03,.23+j*.10),(.11,.02,.022),"black")
  rod("Folded fortune",(.48,0,.16),(.48,0,1.08),.045,"white")
 elif i==5:
  rod("Gohei wooden staff",(0,0,.08),(0,0,1.52),.07,"wood")
  for j in range(5):
   z=.81+j*.14
   for s in (-1,1):box("White shide",(.22*s,0,z),(.37,.025,.11),"white")
 elif i==6:
  rod("Hamaya sacred arrow",(0,0,.04),(0,0,1.70),.043,"wood2")
  cyl("Arrow point",(0,0,1.77),.095,.24,"gold",6,0)
  for s in (-1,1):box("Arrow feather",(.15*s,0,.37),(.22,.02,.34),"white")
 elif i==7:
  for j in range(3):
   x=(j-1)*.49
   box("Shide paper ribbon",(x,0,1.01),(.19,.02,.98),"white")
   for k in range(3):box("Zigzag cut",(x+.13,0,.46+k*.23),(.25,.02,.12),"paper")
  rod("Ceremonial hanging cord",(-.9,0,1.54),(.9,0,1.54),.035,"bamboo")
 elif i==8:
  box("Masu square wooden cup",(0,0,.39),(.86,.86,.70),"wood2")
  box("Open interior",(0,0,.76),(.69,.69,.018),"black")
  for x in (-.39,.39):box("Joinery dovetail",(x,0,.65),(.09,.87,.08),"wood")
 else:
  for r,z in [(.52,.31),(.36,.68)]:orb("Kagami mochi rice cake",(0,0,z),(r,r,.23),"white",2)
  orb("Daidai fruit",(0,0,.94),(.20,.20,.18),"orange")
  orb("Daidai leaf",(.13,0,1.10),(.19,.12,.04),"leaf")
  box("Display stand",(0,0,.08),(1.23,.92,.16),"wood")
