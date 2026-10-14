"""Architecturally detailed shrines, floats, hoko, festival wheels."""
import math
from geometry import *
from parts import *
def make(i):
 if i==9:
  for y in (-.09,.09):wheel("Giant ceremonial hikiyama wheel",0,y,.82,.79,32)
  cyl("Central iron axle",(0,0,.82),.16,.50,"iron",24).rotation_euler.x=math.pi/2
  for s in (-1,1):
   for k in range(16):
    a=T*k/16
    ellipsoid("Chased tire rivet",( .79*math.cos(a),s*.15,.82+.79*math.sin(a)),(.024,.024,.025),"gold",1)
  return
 float_model(i)
 if i==0:
  for x in (-.43,.43):
   for y in (-.33,.33):
    flower("Mikoshi engraved chrysanthemum",(x,y-.06,1.00),.09,"gold")
 elif i==1:
  for k in range(16):
   a=k*T/16
   ellipsoid("Phoenix mikoshi round brass medallions",(.6*math.cos(a),.5*math.sin(a),1.17),(.08,.05,.08),"gold")
 elif i==2:
  for s in (-1,1):
   polygon("Carved danjiri side dragon",[(-.72,s*.65,.73),(-.32,s*.65,1.14),(.19,s*.65,.9),(.66,s*.65,1.24),(.68,s*.65,.78)],"gold",.065)
   for j in range(18):
    x=-.67+j*.076
    rod("Danjiri chiseled eaves", (x,s*.53,1.40),(x,s*.72,1.28),.018,"cedar")
 elif i==3:
  for s in (-1,1):
   for j in range(8):
    x=-.6+j*.17
    ellipsoid("Hikiyama carved gilt floral crest",(x,s*.67,1.0),(.07,.045,.078),"gold",2)
 elif i==4:
  for s in (-1,1):
   for j in range(12):
    z=.57+j*.08
    box("Yatai layered gold curtain trim",(s*.69,-.62,z),(.04,.04,.025),"gold")
 elif i==5:
  for j in range(14):
   a=j*T/14
   strand("Hoko pennant silk fringe",[(.25*math.cos(a),.25*math.sin(a),3.2),
        (.5*math.cos(a),.5*math.sin(a),2.70)],"red",.018)
 elif i==6:
  for j in range(10):
   a=j*T/10
   ellipsoid("Taikodai embroidered knot",(.56*math.cos(a),.54*math.sin(a),1.37),(.10,.06,.10),"gold")
 elif i==7:
  for j in range(18):
   a=j*T/18
   strand("Kasaboko hanging silk streamer",[(.4*math.cos(a),.4*math.sin(a),2.72),
      (.55*math.cos(a),.55*math.sin(a),2.24)],"red",.021)
 elif i==8:
  for j in range(8):
   x=-.52+j*.15
   rod("Lantern tower lacquer grate",(x,-.50,.76),(x,-.50,1.45),.02,"gold")
