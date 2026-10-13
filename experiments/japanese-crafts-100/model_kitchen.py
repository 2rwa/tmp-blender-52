from geometry import *
from geometry_lathe import lathe
def make(i):
 if i==0:lathe("Yunomi tea cup",[(.3,.02),(.38,.06),(.39,.77),(.34,.80),(.29,.76),(.27,.17),(.10,.12)],"clay")
 elif i==1:lathe("Tokkuri bottle",[(.31,.02),(.42,.11),(.44,.50),(.21,.77),(.16,1.0),(.22,1.04)],"white")
 elif i==2:lathe("Ochoko sake cup",[(.14,.02),(.29,.06),(.39,.43),(.36,.46),(.31,.39),(.12,.11)],"blue")
 elif i==3:
  lathe("Suribachi",[(.24,.01),(.42,.06),(.69,.47),(.64,.51),(.55,.43),(.32,.15)],"clay")
  for j in range(20):rod("Groove",(.29,0,.12),(.56,0,.42),.007,"wood2") if j==0 else None
 elif i==4:
  rod("Surikogi pestle",(-.30,0,.10),(.15,0,1.38),.095,"wood2")
  orb("Rounded head",(-.3,0,.13),(.115,.115,.11),"wood")
 elif i==5:
  lathe("Hangiri cedar tub",[(.46,.04),(.59,.07),(.64,.60),(.58,.63),(.54,.57),(.50,.13)],"wood2")
  for z in (.17,.51):ring("Hoop",(0,0,z),.61,.024,"iron")
 elif i==6:
  lathe("Ohitsu rice keeper",[(.46,.01),(.51,.06),(.52,.75),(.49,.79)],"wood2")
  cyl("Round lid",(0,0,.81),.56,.065,"wood");ring("Band",(0,0,.53),.52,.02,"iron")
 elif i==7:
  for z in (.12,.32,.52):
   cyl("Seiro steaming tray",(0,0,z),.55,.18,"bamboo",16)
   ring("Tray edge",(0,0,z+.09),.54,.018,"wood")
  cyl("Seiro lid",(0,0,.72),.60,.06,"bamboo2")
 elif i==8:
  for j in range(3):
   box("Lacquer jubako tier",(0,0,.13+.27*j),(.95,.95,.25),"red")
   box("Gold tier seam",(0,0,.26+.27*j),(1,.98,.028),"gold")
  box("Decorated lid",(0,0,.96),(1.05,1.05,.08),"black")
 else:
  rod("Long shamoji",(0,0,.04),(0,0,.89),.065,"wood2")
  o=orb("Rice paddle blade",(0,0,1.10),(.23,.075,.32),"bamboo")
