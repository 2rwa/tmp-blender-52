import math
from geometry import *
from geometry_lathe import lathe
def make(i):
 if i==0:lathe("Chawan bowl",[(.12,.03),(.43,.06),(.62,.42),(.60,.51),(.53,.50),(.37,.16),(.10,.11)],"clay")
 elif i==1:
  cyl("Whisk grip",(0,0,.19),.13,.38,"bamboo")
  for j in range(28):
   a=j*math.tau/28;rod("Fine bamboo tine",(math.cos(a)*.11,math.sin(a)*.11,.36),(math.cos(a)*.38,math.sin(a)*.38,.9),.009,"bamboo",6)
 elif i==2:
  rod("Tea scoop shaft",(-.7,0,.3),(.56,0,.35),.038,"bamboo")
  orb("Curved scoop",(.67,0,.37),(.23,.14,.055),"bamboo2")
 elif i==3:
  lathe("Lacquer natsume",[(.32,0),(.46,.08),(.50,.34),(.46,.70),(.30,.8)],"red")
  cyl("Golden lid",(0,0,.80),.46,.06,"black");ring("Lacquer rim",(0,0,.78),.43,.018,"gold")
 elif i==4:
  lathe("Cast iron kettle",[(.25,.03),(.59,.14),(.64,.44),(.45,.76),(.24,.84)],"iron")
  cyl("Lid",(0,0,.83),.30,.055,"black");orb("Knob",(0,0,.92),(.08,.08,.08),"gold")
  ring("Arch handle",(0,0,.87),.71,.043,"iron",24,"Y")
 elif i==5:
  lathe("Kyusu body",[(.25,.02),(.54,.1),(.57,.48),(.38,.73)],"clay")
  cyl("Lid",(0,0,.76),.35,.07,"wood2");rod("Side handle",(.45,0,.46),(.95,0,.45),.095,"clay")
  rod("Pouring spout",(-.43,0,.49),(-.80,0,.67),.09,"clay")
 elif i==6:
  lathe("Tea cauldron",[(.35,.05),(.65,.14),(.69,.47),(.56,.79),(.39,.87)],"iron")
  cyl("Cauldron lid",(0,0,.86),.45,.08,"iron");orb("Lid knob",(0,0,.96),(.08,.08,.07),"gold")
  for x in (-.65,.65):ring("Handle ear",(x,0,.56),.13,.033,"gold",12,"Y")
 elif i==7:
  lathe("Water jar",[(.29,0),(.55,.08),(.57,.73),(.47,.90)],"blue")
  cyl("Jar cap",(0,0,.92),.50,.065,"wood");ring("Top gold lip",(0,0,.93),.44,.02,"gold")
 elif i==8:
  cyl("Bamboo dipper cup",(0,0,.20),.27,.38,"bamboo")
  cyl("Open cup shadow",(0,0,.398),.23,.006,"wood")
  rod("Long hishaku handle",(0,0,.30),(1.23,0,.48),.043,"bamboo")
 else:
  lathe("Ceramic lid rest",[(.18,.02),(.36,.08),(.36,.39),(.31,.42),(.27,.36),(.26,.12)],"clay")
  for j in range(4):ring("Rib", (0,0,.12+j*.07),.35,.012,"gold")
