"""Kitchen ware: hand-built mesh profiles and readable characteristic parts."""
import math
from geometry import *
def make(i):
 if i==0:
  revolve("Yunomi tapered glazed vessel",[(.23,.02),(.33,.05),(.37,.22),(.41,.89),(.385,.94),(.32,.92),(.28,.13),(.12,.09)],"celadon")
  hoop("Ground ceramic foot",(0,0,.06),.31,.025,"clay")
  hoop("Subtle rim gold",(0,0,.935),.39,.014,"cream")
  for z in (.19,.33,.47):hoop("Throwing spiral",(0,0,z),.38,.008,"ivory")
 elif i==1:
  revolve("Tokkuri flared neck",[(.22,.04),(.37,.08),(.47,.27),(.48,.56),(.24,.91),(.17,1.19),(.23,1.28),(.21,1.32),(.13,1.30),(.12,1.12)],"ivory")
  hoop("Indigo rim",(0,0,1.30),.22,.024,"indigo")
  for z in (.35,.40):hoop("Sake bottle cobalt wave",(0,0,z),.46,.025,"blue")
  petals("Sake blossom",0,.68,.10,"indigo",5,y=-.44)
 elif i==2:
  revolve("Ochoko footed shallow sake bowl",[(.12,.025),(.25,.04),(.33,.12),(.43,.41),(.41,.46),(.34,.42),(.22,.15),(.11,.11)],"blue")
  hoop("Ochoko fine porcelain lip",(0,0,.455),.42,.018,"ivory")
  hoop("Foot ring",(0,0,.05),.24,.02,"ivory")
  radial("Interior brushstroke",12,.16,.31,.24,"ivory")
 elif i==3:
  revolve("Suribachi heavy conical mortar",[(.27,.02),(.43,.065),(.75,.56),(.73,.62),(.66,.58),(.38,.16),(.17,.13)],"clay",48)
  hoop("Heavy rolled rim",(0,0,.60),.728,.043,"wooddark",40)
  for j in range(64):
   a=j*math.tau/64
   rod("Fine inner grinding ridges",( .31*math.cos(a),.31*math.sin(a),.18),
    (.65*math.cos(a),.65*math.sin(a),.55),.007,"cream",6)
 elif i==4:
  strand("Wooden surikogi softly tapered",[(-.55,0,.09),(-.45,0,.29),(-.18,0,.65),(.04,0,1.07),(.28,0,1.47)],"hinoki",.10)
  ellipsoid("Rounded grinding bulb",(-.55,0,.09),(.14,.14,.13),"cedar")
  for t in range(7):
   x=-.35+t*.10
   rod("Visible cedar grain",(x,-.096,.44+t*.11),(x+.045,-.094,.51+t*.11),.005,"wooddark",6)
 elif i==5:
  revolve("Hangiri wide cedar tub",[(.42,.06),(.67,.08),(.73,.14),(.76,.64),(.72,.69),(.65,.63),(.61,.16),(.32,.13)],"hinoki",40)
  ribs("Individual wooden staves",32,.75,.12,.64,"cedar",.015)
  for z in (.18,.48,.61):hoop("Blackened copper binding",(0,0,z),.751,.026,"iron",44)
  radial("Visible wood bottom joints",12,.24,.57,.14,"cedar")
 elif i==6:
  revolve("Ohitsu straight-grained rice container",[(.36,.04),(.55,.08),(.56,.82),(.53,.88),(.48,.85)],"hinoki",36)
  cyl("Thick removable wooden rice lid",(0,0,.92),.60,.12,"cedar",32)
  ribs("Vertical cedar strips",28,.56,.11,.80,"cedar",.016)
  for z in (.18,.69):hoop("Dark bamboo vessel hoops",(0,0,z),.569,.025,"bamboodark")
  box("Small lifting handle",(0,0,1.02),(.33,.12,.12),"hinoki")
 elif i==7:
  for k in range(3):
   z=.16+k*.25
   revolve("Stacked bamboo seiro tray",[(.42,z-.10),(.59,z-.095),(.59,z+.105),(.54,z+.114),(.50,z+.06)],"bamboo",32)
   ribs("Steam basket reeds",24,.59,z-.09,z+.08,"hinoki",.009)
   hoop("Seiro reinforcing lip",(0,0,z+.1),.57,.025,"cedar")
  cyl("Bamboo steamer lid",(0,0,.91),.63,.065,"bamboo",32)
  radial("Lid radial grain",20,.05,.61,.95,"hinoki")
 elif i==8:
  for k in range(3):
   z=.19+k*.28
   box("Jubako lacquered tier",(0,0,z),(1.06,.99,.27),"red",.047)
   box("Jubako thin gold seam",(0,0,z+.13),(1.08,1.01,.025),"gold",.004)
  box("Black jubako top lid",(0,0,1.06),(1.14,1.06,.095),"lacquer",.042)
  petals("Gold chrysanthemum on lid",0,1.115,.16,"gold",6,y=-.0)
 elif i==9:
  strand("Carved rice paddle neck",[(0,0,.11),(0,0,.35),(0,0,.62)],"hinoki",.073)
  ellipsoid("Wide flattened shamoji blade",(0,0,1.07),(.32,.060,.49),"hinoki",2)
  for s in (-1,1):
   rod("Rice paddle carved outline",(s*.25,-.042,.83),(s*.23,-.042,1.34),.015,"cedar",6)
  for k in range(9):
   z=.79+k*.065
   rod("Rough wooden grain",(-.17,-.060,z),(.17,-.060,z),.006,"cedar",6)
