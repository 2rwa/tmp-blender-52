"""Traditional household objects: fixtures, fittings, folded screens, and textiles."""
import math
from geometry import *
def make(i):
 if i==0:
  box("Andon glowing washi", (0,0,.82),(.83,.70,1.33),"washi",.005)
  for x in (-.47,.47):
   for y in (-.4,.4):
    box("Fine timber corner stile",(x,y,.84),(.073,.07,1.60),"cedar")
  for z in (.09,.45,.83,1.21,1.58):
   box("Traditional paper frame horizontal",(0,-.415,z),(.95,.063,.052),"wooddark")
   box("Rear wooden horizontal",(0,.415,z),(.95,.063,.05),"cedar")
  for x in (-.27,0,.27):
   box("Vertical lattice",(x,-.421,.84),(.027,.036,1.46),"cedar")
  box("Andon broad foot", (0,0,.055),(1.08,.91,.11),"wooddark")
 elif i==1:
  for k in range(16):
   z=.16+k*.087
   r=.28+.27*math.sin(math.pi*(k+.5)/16)
   cyl("Concertina chochin red rib"+str(k),(0,0,z),r,.087,"red",36)
   hoop("Bamboo rib seam"+str(k),(0,0,z+.043),r,.013,"wooddark",40)
  cyl("Chochin top cap",(0,0,1.59),.285,.095,"lacquer")
  cyl("Chochin bottom cap",(0,0,.10),.285,.09,"lacquer")
  hoop("Wire hanging ring",(0,0,1.75),.115,.028,"steel",20,"Y")
  ellipsoid("Handpainted white circle",(0,-.545,.91),(.20,.025,.26),"washi")
 elif i==2:
  revolve("Bonbori hexagonal paper shade",[(.11,.70),(.36,.72),(.56,.91),(.52,1.27),(.32,1.48),(.09,1.50)],"washi",6)
  for j in range(6):
   a=j*math.tau/6
   rod("Hexagonal bonbori frame",( .50*math.cos(a),.50*math.sin(a),.99),
     (.31*math.cos(a),.31*math.sin(a),1.47),.024,"cedar")
  cyl("Bonbori brass stem",(0,0,.38),.052,.76,"wooddark")
  revolve("Snow-cave lamp pedestal",[(.42,.045),(.44,.08),(.27,.11),(.13,.19)],"wooddark")
 elif i==3:
  revolve("Hibachi deep glazed ash bowl",[(.41,.05),(.68,.11),(.72,.65),(.64,.77),(.58,.72),(.53,.19),(.22,.14)],"clay",40)
  hoop("Hibachi dark copper lip",(0,0,.73),.66,.049,"bronze",40)
  cyl("Gray ash inside",(0,0,.50),.49,.035,"charcoal",32)
  for j in range(7):
   a=j*math.tau/7
   ellipsoid("Charcoal briquette",( .35*math.cos(a),.35*math.sin(a),.57),(.17,.14,.12),"black")
  for z in (.15,.30):hoop("Brazier ornate bands",(0,0,z),.69,.015,"cream")
 elif i==4:
  for x in (-.84,.84):
   for y in (-.51,.51):
    rod("Fine kaya mosquito-net corner",(x,y,.08),(x,y,1.80),.017,"ivory")
  box("Kaya woven ceiling",(0,0,1.80),(1.72,1.07,.022),"washi",.003)
  for j in range(18):
   x=-.84+j*.099
   rod("Microscopic mosquito net front thread",(x,-.51,.08),(x,-.51,1.78),.006,"ivory",6)
  for j in range(14):
   z=.12+j*.12
   rod("Mosquito net weft",(-.83,-.51,z),(.83,-.51,z),.006,"ivory",6)
  for x in (-.84,.84):
   strand("Corner tie",[(x,-.51,1.8),(x*.8,-.51,2.0),(x*.5,0,2.1)],"cedar",.016)
 elif i==5:
  rod("Noren upper curtain rod",(-1.04,0,1.63),(1.04,0,1.63),.047,"cedar")
  for j in range(3):
   x=-.71+j*.71
   textile("Noren indigo cloth", (x,-.025,.91),(.65,.04,1.29),"indigo",9)
   for k in range(4):
    ellipsoid("White dyed family crest",(x+(k-1.5)*.075,-.06,1.23),(.029,.011,.052),"washi")
   box("Noren lower seam",(x,-.052,.27),(.64,.024,.025),"blue")
  for j in range(7):
   x=-.91+j*.32
   strand("Noren suspension",[(x,0,1.52),(x,0,1.70)],"ivory",.012)
 elif i==6:
  for j in range(4):
   x=(j-1.5)*.54;y=.07*(j%2)
   box("Folding byobu paper screen",(x,y,.83),(.49,.055,1.43),"washi",.006)
   for zz in (.09,1.57):box("Byobu top-bottom rail",(x,y,zz),(.55,.075,.047),"wooddark")
   for s in (-1,1):box("Black lacquer frame",(x+s*.265,y,.83),(.037,.085,1.56),"wooddark")
   polygon("Byobu stylized mountain"+str(j),[(x-.23,y-.04,.48),(x-.03,y-.04,1.0),(x+.22,y-.04,.48)],"celadon",.019)
   ellipsoid("Gold rising sun",(x+.16,y-.07,1.21),(.08,.02,.08),"gold")
  for j in range(3):rod("Hinge",(j*.54-.54,0,.11),(j*.54-.54,0,1.49),.016,"bronze")
 elif i==7:
  box("Tatami straw woven panel",(0,0,.10),(1.95,1.08,.18),"straw",.024)
  for y in (-.48,.48):box("Deep indigo tatami border",(0,y,.19),(1.98,.09,.025),"indigo",.003)
  for j in range(34):
   x=-.93+j*.055
   rod("Individual woven grass reed",(x,-.43,.199),(x,.43,.199),.006,"hinoki",6)
  for x in (-.92,.92):
   for y in (-.46,.46):ellipsoid("Corner binding stud",(x,y,.215),(.025,.025,.01),"gold",1)
 elif i==8:
  box("Zabuton plush filled sitting cushion",(0,0,.23),(1.20,1.20,.36),"fabric",.11)
  box("Seamed indigo zabuton center",(0,0,.416),(1.10,1.10,.025),"indigo",.034)
  for s in (-1,1):
   for t in (-1,1):
    ellipsoid("Corner tassel",(.58*s,.58*t,.18),(.13,.1,.07),"gold")
  ellipsoid("Central stitched button",(0,0,.44),(.058,.058,.025),"gold")
  for j in range(8):
   x=-.47+j*.14
   rod("Fine woven seam",(x,-.58,.23),(x,-.58,.35),.007,"washi",6)
 elif i==9:
  revolve("Furin handblown glass chime",[(.12,.60),(.34,.66),(.39,.90),(.29,1.23),(.11,1.31),(.07,1.24),(.29,.93),(.31,.73)],"blue",36)
  hoop("Glass lower beaded rim",(0,0,.69),.338,.030,"ivory")
  rod("Thin hanging string",(0,0,.64),(0,0,1.66),.014,"wooddark",8)
  ellipsoid("Inside clapper",(0,0,.74),(.095,.095,.08),"gold")
  box("White rectangular wind sail",(0,0,.35),(.25,.022,.43),"washi",.009)
  petals("Painted flower on chime",0,1.03,.10,"ivory",5,y=-.36)
