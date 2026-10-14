"""Traditionally built performance props and timber stage installations."""
import math
from geometry import *
from parts import *
def make(i):
 if i==0:shrine_gate("Faithful miniature lacquer torii",1.9,2.2)
 elif i==1:
  box("Kabuki stage kagamiita cedar frame",(0,0,1.02),(1.87,.14,1.89),"wooddark",.028)
  box("Kagamiita pale paper field",(0,-.09,1.01),(1.72,.03,1.72),"washi")
  strand("Painted old pine trunk",[(-.73,-.15,.22),(-.49,-.15,.59),(-.30,-.15,1.19),
    (.03,-.15,1.39),(.54,-.15,1.63)],"wooddark",.10)
  for j in range(38):
   a=T*j/38
   ellipsoid("Fine painted pine needle mass",(.53*math.cos(a),-.18,1.25+.39*math.sin(a)),(.13,.022,.045),"green")
 elif i==2:
  for j in range(6):
   x=(j-2.5)*.39
   box("Standing six panel byobu gold leaf",(x,0,1.0),(.37,.07,1.86),"gold",.025)
   for s in (-1,1):box("Black lacquer border",(x+s*.19,-.01,1.0),(.026,.085,1.86),"wooddark")
   for z in (.12,1.91):box("Gold frame top and bottom",(x,-.03,z),(.39,.08,.03),"wooddark")
   for k in range(3):
    a=.6*k+j
    ellipsoid("Byobu painted blossom", (x+.10*math.sin(a),-.060,.63+.35*k),(.10,.020,.10),"pink")
 elif i==3:
  revolve("Bonbori hexagonal washi lantern shade",[(.22,.68),(.39,.75),(.61,1.02),(.54,1.34),(.24,1.53)],"washi",6)
  for j in range(6):
   a=T*j/6
   rod("Bonbori black timber framing",(.54*math.cos(a),.54*math.sin(a),1.02),
        (.24*math.cos(a),.24*math.sin(a),1.53),.028,"wooddark")
  pole("Snow lantern pedestal",1.00,"cedar")
  box("Snow lantern hex-style stage plinth",(0,0,.07),(.82,.75,.14),"wooddark")
 elif i==4:
  box("Andon glowing shoji paper",(0,0,.94),(.95,.74,1.60),"washi",.006)
  for s in (-1,1):
   for t in (-1,1):box("Corner architectural bamboo",(s*.46,t*.37,.97),(.075,.08,1.83),"cedar")
  for z in (.13,.47,.82,1.17,1.54,1.86):
   box("Andon traditional horizontal crossbeams",(0,-.40,z),(.97,.09,.055),"wooddark")
  for x in (-.29,0,.29):box("Andon inner mullion",(x,-.42,.96),(.023,.035,1.65),"hinoki")
  box("Andon wooden base",(0,0,.06),(1.13,.90,.12),"wooddark")
 elif i==5:
  pole("Festival noren silk curtain hanging rod",1.92,"cedar",-1.03,0,.04)
  rod("Actual curtain rod",(-1.15,0,1.83),(1.15,0,1.83),.061,"wooddark")
  for j in range(4):
   x=-.80+j*.53
   textile("Individual noren dyed panel",(x,0,.99),(.48,.036,1.49),"red" if j%2 else "washi",12)
   flower("Festival textile family mon",(x,-.032,1.25),.10,"gold")
  for j in range(8):
   x=-.99+j*.28
   strand("Noren suspension thread",[(x,0,1.74),(x,0,1.91)],"ivory",.014)
 elif i==6:
  for z,w in [(0.21,2.15),(1.47,1.95),(2.62,1.85)]:
   box("Full-size yagura cantilever floor",(0,0,z),(w,w,.16),"cedar",.036)
   gridbeams("Yagura structural deck",w,w,z+.10,"hinoki",12)
  for x in (-.82,.82):
   for y in (-.82,.82):
    box("Large ceremonial yagura timber pillars",(x,y,1.45),(.13,.14,2.84),"wooddark")
    for z in (.49,.92,1.62,2.20):ellipsoid("Mortise tenon bolt",(x,y,z),(.079,.08,.047),"gold")
  for z in (.9,2.28):
   for s in (-1,1):
    box("Upper balcony guard rails",(0,s*.85,z),(1.98,.065,.085),"red")
    for j in range(12):
     x=-.85+j*.154
     rod("Upper yagura balustrade",(x,s*.85,z-.55),(x,s*.85,z),.023,"gold")
  roof("High festival yagura roof",2.80,2.0,2.0,.49,"lacquer",1)
  lantern("Yagura performance lantern left",-.62,-.85,1.78,.55)
  lantern("Yagura performance lantern right",.62,-.85,1.78,.55)
  drum("Yagura ensemble taiko",(0,0,2.72),.29,.45,"Y","red")
 elif i==7:
  rod("Horizontal festival lantern cable",(-1.55,0,1.72),(1.55,0,1.72),.025,"black")
  for j in range(7):
   x=-1.40+j*.46
   lantern("Individual hanging lantern row",x,0,1.12,.64,"red" if j%2 else "washi")
 elif i==8:
  rod("Red-and-white ceremony curtain rod",(-1.29,0,1.79),(1.29,0,1.79),.052,"cedar")
  for j in range(14):
   x=-1.19+j*.184
   box("Separate white or red kōhaku curtain stripe",(x,0,.88),(.17,.035,1.68),
      "red" if j%2 else "washi",.006)
   for k in range(7):
    z=.19+k*.23
    ellipsoid("Stage curtain stitch",(x,-.027,z),(.013,.013,.017),"gold",1)
  fringe("Kōhaku festive curtain edge",0,-.03,.09,2.49,38,"gold")
 elif i==9:
  box("Carved performance drum stand upper deck",(0,0,.88),(1.52,.84,.17),"cedar",.05)
  for s in (-1,1):
   rod("Crossed taiko stand legs",(s*.64,-.31,.05),(-s*.43,-.25,.82),.082,"wooddark")
   rod("Laced drum support",(s*.64,.31,.05),(-s*.43,.25,.82),.082,"cedar")
  for k in range(11):
   x=-.60+k*.12
   rod("Wood tabletop grooves",(x,-.32,.98),(x,.32,.98),.01,"gold")
