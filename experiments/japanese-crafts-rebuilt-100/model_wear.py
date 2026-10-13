"""Wearable handcrafts: patterned forms and structural attachments."""
import math
from geometry import *
def arc_fan(name,span=math.pi,ro=.98,ri=.15,parts=24):
 for j in range(parts):
  a=math.pi/2-span/2+span*j/parts
  b=math.pi/2-span/2+span*(j+1)/parts
  polygon(name+str(j),[(ri*math.cos(a),0,.12+ri*math.sin(a)),
   (ro*math.cos(a),0,.12+ro*math.sin(a)),
   (ro*math.cos(b),0,.12+ro*math.sin(b)),
   (ri*math.cos(b),0,.12+ri*math.sin(b))],"washi" if j%3 else "red",.023)
  rod("Folded fan rib",(.02,0,.12),(ro*math.cos(a),-.03,.12+ro*math.sin(a)),.014,"cedar",8)
def make(i):
 if i==0:
  arc_fan("Individual washi fan pleat",math.pi*.98,1.02,.19,28)
  ellipsoid("Gold rivet for pivot",(0,-.05,.12),(.08,.04,.08),"gold")
  for k in range(8):
   a=math.pi/2-math.pi*.98/2+k*math.pi*.98/8
   ellipsoid("Delicate fan ink pattern",(.76*math.cos(a),-.02,.12+.76*math.sin(a)),(.05,.015,.03),"indigo")
 elif i==1:
  ellipsoid("Uchiwa stiff paper leaf",(0,0,1.05),(.69,.045,.64),"washi",3)
  rod("Bamboo uchiwa handle",(0,0,.04),(0,0,.83),.065,"bamboo",18)
  for j in range(17):
   a=j*math.pi/16
   rod("Spreading bamboo veins",(0,-.05,.71),(.62*math.cos(a),-.05,1.05+.51*math.sin(a)),.010,"bamboodark",6)
  petals("Uchiwa print blossom",0,1.08,.18,"red",7,y=-.05)
 elif i==2:
  rod("Wagasa bamboo shaft",(0,0,.06),(0,0,1.95),.073,"cedar",18)
  for j in range(24):
   a=j*math.tau/24;b=(j+1)*math.tau/24
   polygon("Wagasa curved red canopy",[(0,0,1.77),
    (.49*math.cos(a),.49*math.sin(a),1.67),
    (1.02*math.cos(a),1.02*math.sin(a),1.31),
    (1.02*math.cos(b),1.02*math.sin(b),1.31),
    (.49*math.cos(b),.49*math.sin(b),1.67)],"red" if j%3 else "vermilion",.015)
   rod("Wagasa radial bamboo bone",(0,0,1.77),
       (1.02*math.cos(a),1.02*math.sin(a),1.31),.014,"wooddark")
   rod("Wagasa internal stretcher",(0,0,1.15),(.49*math.cos(a),.49*math.sin(a),1.67),.013,"hinoki")
  hoop("Wagasa sliding runner",(0,0,1.14),.15,.03,"bronze")
 elif i==3:
  for sign in (-1,1):
   x=.38*sign
   box("Carved geta sole",(x,0,.42),(.58,1.09,.15),"hinoki",.085)
   for y in (-.35,.31):box("Two geta teeth",(x,y,.20),(.54,.17,.35),"cedar",.018)
   strand("Cloth thong",[ (x-.22,-.24,.51),(x-.07,.09,.69),(x,.26,.67),
     (x+.21,-.23,.51)],"red",.049)
   for yy in (-.44,.44):box("Raised wood grain",(x,yy,.50),(.43,.011,.015),"wooddark",.002)
 elif i==4:
  for x in (-.38,.38):
   ellipsoid("Woven zori sole",(x,0,.13),(.32,.60,.16),"straw",3)
   for j in range(11):
    z=-.48+j*.096
    rod("Weave crossline",(x-.22,z,.23),(x+.22,z,.23),.011,"hinoki")
   strand("Soft zori hanao",[(x-.24,-.13,.24),(x,.23,.49),(x+.24,-.13,.24)],"indigo",.046)
 elif i==5:
  for x in (-.33,.33):
   ellipsoid("Tabi ankle wrap",(x,.24,.51),(.27,.25,.42),"ivory",3)
   ellipsoid("Distinct tabi heel",(x,-.18,.20),(.28,.39,.18),"washi",3)
   ellipsoid("Split tabi big toe",(x-.12,-.50,.14),(.13,.19,.11),"ivory",2)
   ellipsoid("Split other toes",(x+.10,-.45,.14),(.16,.20,.11),"washi",2)
   for j in range(5):ellipsoid("Back fastening hook",(x,.43,.29+j*.10),(.026,.014,.015),"black",1)
 elif i==6:
  rod("Kanzashi lacquer hair stick",(-.77,0,.12),(.47,0,1.45),.044,"lacquer")
  for j in range(8):
   a=j*math.tau/8
   ellipsoid("Complex gold petal",(.45+.24*math.cos(a),-.04,1.43+.24*math.sin(a)),
     (.13,.042,.18),"pink")
  ellipsoid("Kanzashi flower pearl",(.45,-.09,1.43),(.10,.08,.10),"gold")
  for j in range(5):strand("Small dangling chain",[(.55+j*.045,0,1.28),(.58+j*.05,0,1.04),(.59+j*.05,0,.90)],"gold",.015)
 elif i==7:
  ellipsoid("Kinchaku rounded textile body",(0,0,.57),(.60,.47,.59),"indigo",3)
  cyl("Gathered bag neck",(0,0,1.04),.32,.16,"fabric",26,top=.24)
  for j in range(28):
   a=j*math.tau/28
   rod("Kinchaku folded cloth seam",(.50*math.cos(a),.39*math.sin(a),.36),
     (.26*math.cos(a),.28*math.sin(a),1.06),.012,"blue")
  hoop("Braided silk closure",(0,0,1.13),.25,.035,"gold")
  strand("Double drawcord",[(-.2,0,1.12),(-.42,0,1.40),(0,0,1.57),(.40,0,1.41),(.2,0,1.12)],"red",.034)
 elif i==8:
  box("Wrapped gift parcel",(0,0,.47),(1.04,.98,.75),"cedar",.08)
  box("Blue furoshiki cross fold",(0,0,.89),(.35,1.06,.08),"indigo",.06)
  box("Blue furoshiki cross fold",(0,0,.93),(1.09,.31,.07),"blue",.05)
  for s in (-1,1):
   strand("Tied furoshiki bow",[(s*.12,0,1.0),(s*.49,0,1.26),(s*.49,0,1.47),(0,0,1.13)],"blue",.11)
  ellipsoid("Knotted silk center",(0,0,1.12),(.20,.15,.16),"indigo")
 elif i==9:
  textile("Traditional narrow tenugui",(0,0,.79),(1.42,.035,1.44),"washi",20)
  for j in range(8):
   x=-.60+j*.17
   rod("Vertical indigo dyed stripe",(x,-.030,.15),(x,-.030,1.44),.026,"indigo",6)
  for y in (.09,1.49):rod("Fine woven hemming",(-.71,-.03,y),(.71,-.03,y),.017,"red")
  for j in range(12):
   x=-.66+j*.115
   rod("Fringed tenugui edge",(x,0,.065),(x,0,.02),.008,"ivory",6)
