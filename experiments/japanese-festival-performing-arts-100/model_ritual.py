"""Ten distinct shrine-festival instruments and ritual structures."""
import math
from geometry import *
from parts import *
def make(i):
 if i==0:
  lantern("Festival red chouchin",scale=1.6)
  for z in (.45,1.90):hoop("Decorative cord coupler",(0,0,z),.25,.03,"gold")
 elif i==1:
  pole("Takachochin tall bamboo shaft",2.9,"cedar",0,0,.061)
  lantern("Takachochin high lantern",0,0,2.48,1.1,"red")
  for j in range(12):
   a=j*T/12
   strand("Lantern pole banner cord",[(0,0,2.88),(.16*math.cos(a),.16*math.sin(a),2.5)],"gold",.012)
 elif i==2:
  shrine_gate("Sacred shimenawa gateway",1.8,2.0)
  for j in range(3):
   phase=j*T/3
   points=[]
   for k in range(75):
    t=k/74
    x=-.72+1.44*t
    points.append((x,-.16+.047*math.cos(22*T*t+phase),1.54+.04*math.sin(22*T*t+phase)))
   strand("Twisted shimenawa core",points,"straw",.043)
  for x in (-.50,0,.50):
   polygon("Hanging white zigzag shide",[(x-.05,-.2,1.50),(x+.09,-.2,1.50),(x+.09,-.2,1.30),(x+.2,-.2,1.30),
      (x+.2,-.2,1.1),(x-.02,-.2,1.1)],"washi",.02)
 elif i==3:
  box("Bound shide top stave",(0,0,1.70),(.85,.085,.11),"cedar")
  for j in range(13):
   x=-.41+j*.069
   polygon("White zigzag streamer",[(x-.03,-.07,1.62),(x+.025,-.07,1.62),(x+.07,-.07,1.36),
    (x-.02,-.07,1.25),(x+.06,-.07,1.0),(x-.045,-.07,.67)],"washi",.012)
 elif i==4:
  pole("Sakaki sacred stem",1.5,"cedar",0,0,.044)
  for j in range(32):
   z=.3+j*.044;a=j*2.4
   rod("Branchlet",(0,0,z),(.33*math.cos(a),.33*math.sin(a),z+.16),.016,"bamboodark")
   ellipsoid("Sakaki evergreen leaf",(.36*math.cos(a),.36*math.sin(a),z+.20),(.13,.07,.049),"green")
  hoop("Sacred branch binding",(0,0,.15),.06,.026,"washi")
 elif i in (5,6):
  shrine_gate("Shrine hanging offerings rack",1.5,1.9)
  for row in range(3):
   z=.40+row*.42
   rod("Horizontal offering rack",(-.72,-.10,z),(.72,-.10,z),.042,"cedar")
   for j in range(6):
    x=-.61+j*.24
    if i==5:polygon("Individual votive ema plaque",[(x-.10,-.16,z-.06),(x+.10,-.16,z-.06),
       (x+.10,-.16,z-.27),(x,-.16,z-.34),(x-.10,-.16,z-.27)],"hinoki",.03)
    else:
     polygon("Individual omamori pouch",[(x-.085,-.17,z-.07),(x+.085,-.17,z-.07),
      (x+.09,-.17,z-.32),(x,-.17,z-.42),(x-.09,-.17,z-.32)],"red" if j%2 else "indigo",.044)
 elif i==7:
  box("Heavy saisen offering box",(0,0,.62),(1.5,.9,1.06),"cedar",.07)
  for k in range(14):
   x=-.68+k*.105
   rod("Sloped saisen receiving grate",(x,-.47,1.13),(x,.47,1.29),.045,"hinoki",8)
  for y in (-.43,.43):box("Box bronze rail",(0,y,.98),(1.57,.06,.09),"bronze")
  flower("Shrine gilt crest",(0,-.5,.64),.16,"gold")
 elif i==8:
  revolve("Bamboo ladle deep water cup",[(.19,.05),(.29,.08),(.30,.46),(.28,.50),(.24,.45),(.20,.17)],"bamboo")
  rod("Long bamboo ladle handle",(.13,0,.30),(1.65,0,.72),.070,"hinoki",18)
  for x in (.55,1.12):hoop("Ladle handle joints",(x,0,.28+.256*x),.075,.018,"bamboodark",20,"X")
 elif i==9:
  box("Stone lantern square plinth",(0,0,.1),(.89,.84,.2),"charcoal",.05)
  box("Stone lantern upright pedestal",(0,0,.66),(.34,.37,.94),"charcoal",.04)
  box("Carved shrine stone lamp body",(0,0,1.21),(.73,.73,.54),"ivory",.08)
  for s in (-1,1):
   box("Open lantern aperture",(s*.37,0,1.23),(.015,.39,.3),"black")
   box("Open lantern back",(0,s*.37,1.23),(.37,.015,.28),"black")
  roof("Hipped festival lantern cap",1.56,.87,.86,.35,"charcoal")
