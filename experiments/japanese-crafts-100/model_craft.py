import math
from geometry import *
from geometry_lathe import lathe
from geometry_panel import fan
def make(i):
 if i==0:
  lathe("Bronze incense burner",[(.33,.06),(.52,.12),(.57,.67),(.48,.83),(.29,.87)],"iron")
  cyl("Incense burner lid",(0,0,.88),.50,.08,"gold")
  for j in range(3):
   a=j*math.tau/3;cyl("Brazier foot",(.36*math.cos(a),.36*math.sin(a),.10),.10,.19,"gold")
  orb("Openwork lid knob",(0,0,1.01),(.12,.12,.12),"gold")
 elif i==1:
  lathe("Orin resonant singing bowl",[(.25,.06),(.45,.16),(.55,.49),(.47,.56),(.39,.44),(.24,.12)],"gold")
  cyl("Orin cushion",(0,0,.08),.48,.17,"red")
  rod("Wooden striker",(-.85,0,.20),(-.25,0,.45),.065,"wood2")
 elif i==2:
  orb("Mokugyo hollow wooden body",(0,0,.57),(.64,.49,.53),"wood",2)
  orb("Carved fish mouth",(0,-.47,.56),(.41,.045,.22),"black")
  rod("Wooden mallet",(-.72,0,.11),(-.20,0,.89),.075,"wood2")
  orb("Mallet head",(-.20,0,.89),(.17,.17,.15),"red")
 elif i==3:
  lathe("Kiriko faceted glass",[(.26,.05),(.35,.08),(.49,.96),(.45,1.0),(.38,.89),(.26,.15)],"blue",10)
  for j in range(5):ring("Faceted cut",(0,0,.20+j*.14),.30+j*.036,.013,"white",10)
 elif i==4:
  lathe("Shikki lacquer bowl",[(.23,.04),(.47,.12),(.62,.53),(.59,.59),(.52,.51),(.23,.19)],"red")
  ring("Gold lacquer lip",(0,0,.57),.60,.023,"gold")
  cyl("Black foot rim",(0,0,.035),.25,.07,"black")
 elif i==5:
  box("Makie lacquer jewelry box",(0,0,.36),(1.16,.78,.64),"black")
  box("Gold painted lid",(0,0,.70),(1.22,.83,.07),"red")
  for j in range(5):orb("Gold leaf motif",(-.40+j*.18,-.06,.75),(.055,.16,.017),"gold")
 elif i==6:
  fan("Kabuto armored crest",.76,.64,12,"gold")
  orb("Kabuto helmet shell",(0,0,.62),(.55,.42,.48),"iron",2)
  for s in (-1,1):orb("Kabuto side plate",(s*.43,-.04,.49),(.22,.15,.35),"red")
  cyl("Helmet pedestal",(0,0,.10),.54,.19,"wood")
 elif i==7:
  cyl("Kazaridaru sake cask",(0,0,.58),.58,1.14,"wood2",16)
  for z in (.15,.4,.77,1.0):ring("Rope binding",(0,0,z),.58,.03,"bamboo")
  box("Cask paper front",(0,-.591,.60),(.52,.025,.62),"paper")
  orb("Red sake label crest",(0,-.616,.60),(.21,.013,.20),"red")
 elif i==8:
  lathe("Cast tin sake carafe",[(.25,.04),(.45,.12),(.43,.69),(.24,.84),(.24,1.10)],"gray",14)
  rod("Sake carafe spout",(-.18,0,.93),(-.47,0,1.04),.13,"gray")
  ring("Decorative lip",(0,0,1.1),.24,.026,"gold")
 else:
  for j in range(5):
   x=-.37+j*.19
   bend("Braided kumihimo",[ (x-.09,0,.10),(x+.09,0,.40),(x-.09,0,.70),(x+.09,0,1.0),(x-.09,0,1.3) ],["red","gold","blue","paper","indigo"][j],.044)
  ring("Kumihimo loop",(0,0,1.33),.47,.045,"gold",16,"Y")
