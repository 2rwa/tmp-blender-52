import math
from geometry import *
from geometry_lathe import lathe
def make(i):
 if i==0:
  lathe("Woven zaru",[(.28,.04),(.52,.09),(.72,.43),(.69,.49),(.60,.42),(.27,.13)],"bamboo")
  for j in range(5):ring("Woven band",(0,0,.11+j*.07),.34+j*.064,.012,"wood2")
 elif i==1:
  cyl("Tall bamboo basket",(0,0,.43),.48,.82,"bamboo",16)
  for j in range(4):ring("Woven ring",(0,0,.16+j*.18),.49,.020,"wood")
  bend("Basket handle",[(-.45,0,.77),(-.38,0,1.2),(0,0,1.40),(.38,0,1.2),(.45,0,.77)],"wood2",.045)
 elif i==2:
  cyl("Flower bamboo stalk",(0,0,.53),.27,1.06,"bamboo2",12)
  ring("Cut upper rim",(0,0,1.07),.24,.034,"bamboo")
  for z in (.2,.64):ring("Bamboo node",(0,0,z),.27,.03,"wood2")
 elif i==3:
  box("Bamboo craft case",(0,0,.30),(1.12,.78,.58),"bamboo")
  for j in range(8):box("Weave stripe",(-.49+j*.14,-.40,.45),(.045,.06,.40),"wood2")
  box("Top woven lid",(0,0,.63),(1.18,.84,.09),"wood")
 elif i==4:
  for j in range(22):rod("Sudare reed",(-1.0+j*.095,0,.03),(-1+j*.095,0,1.3),.045,"bamboo",6)
  for z in (.17,.6,1.13):rod("Woven cord",(-1.04,-.06,z),(1.04,-.06,z),.014,"wood")
 elif i==5:
  cyl("Tea storage cylinder",(0,0,.48),.43,.94,"bamboo",16)
  cyl("Tea container cap",(0,0,.98),.46,.18,"wood")
  ring("Cap seam",(0,0,.9),.46,.02,"gold")
 elif i==6:
  cyl("Bamboo water scoop",(0,0,.45),.32,.90,"bamboo2",10)
  ring("Lip",(0,0,.9),.31,.035,"wood2")
  rod("Bamboo pouring spout",(.28,0,.69),(.80,0,.89),.09,"bamboo")
 elif i==7:
  rod("Shinobue flute",(-1,0,.14),(1,0,.14),.11,"bamboo",12)
  for j in range(7):orb("Finger hole",(-.65+j*.20,-.10,.14),(.042,.02,.04),"black")
  for x in (-.93,.91):ring("Flute binding",(x,0,.14),.10,.02,"wood",10,"X")
 elif i==8:
  rod("Bamboo dragonfly stem",(0,0,.02),(0,0,1.0),.035,"wood")
  for s in (-1,1):rod("Dragonfly rotor",(0,0,1.00),(.82*s,0,1.05),.13,"bamboo")
 else:
  rod("Broom pole",(0,0,.34),(0,0,1.61),.072,"bamboo")
  for j in range(25):
   a=j*math.tau/25;rod("Straw",(0,0,.51),(.36*math.cos(a),.36*math.sin(a),.02),.018,"wood2",5)
  ring("Broom binding",(0,0,.49),.15,.06,"red")
