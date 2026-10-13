"""Bamboo craft: woven construction, reed spacing and wood nodes."""
import math
from geometry import *
def make(i):
 if i==0:
  revolve("Handwoven shallow zaru basket",[(.25,.035),(.42,.07),(.58,.18),(.78,.48),(.76,.54),(.69,.48),(.50,.25),(.22,.14)],"bamboo",40)
  for z,r in [(.17,.49),(.24,.55),(.33,.65),(.44,.74)]:
   hoop("Concentric bamboo weave",(0,0,z),r,.018,"hinoki",40)
  radial("Zaru radial strips",44,.14,.78,.43,"bamboodark")
  hoop("Basket thick polished binding",(0,0,.53),.758,.043,"cedar",40)
 elif i==1:
  revolve("Tall cylindrical bamboo basket",[(.25,.045),(.42,.05),(.48,.12),(.47,.88),(.46,.94),(.39,.88),(.39,.14)],"straw",36)
  ribs("Vertical woven bamboo ribs",38,.47,.1,.90,"bamboodark",.018)
  for k in range(10):hoop("Horizontal basket weft",(0,0,.12+k*.08),.475,.021,"bamboo",40)
  strand("Bent carrying handle",[(-.48,0,.81),(-.53,0,1.16),(-.31,0,1.43),(0,0,1.52),(.31,0,1.43),(.53,0,1.16),(.48,0,.81)],"cedar",.07)
 elif i==2:
  revolve("Bamboo flower tube",[(.19,.04),(.30,.06),(.31,1.16),(.28,1.18),(.23,1.10),(.22,.12)],"bamboo")
  for z in (.20,.73,1.12):hoop("Natural bamboo joint",(0,0,z),.313,.027,"bamboodark")
  for j in range(14):
   a=j*math.tau/14
   rod("Bamboo fiber",( .303*math.cos(a),.303*math.sin(a),.1),
      (.303*math.cos(a),.303*math.sin(a),1.12),.006,"hinoki",6)
 elif i==3:
  box("Woven rectangular bamboo box",(0,0,.41),(1.24,.88,.78),"bamboo",.07)
  box("Fitted bamboo case lid",(0,0,.83),(1.33,.97,.10),"cedar",.045)
  for j in range(12):
   x=-.54+j*.098
   box("Vertical woven faces",(x,-.46,.45),(.035,.026,.67),"hinoki",.005)
  for j in range(10):
   z=.12+j*.065
   box("Horizontal woven bands",(0,-.47,z),(1.13,.022,.018),"bamboodark",.005)
  box("Lid wooden knob",(0,0,.92),(.28,.17,.09),"hinoki")
 elif i==4:
  for j in range(30):
   x=-1.04+j*.071
   rod("Split sudare reed",(x,0,.05),(x,0,1.45),.028,"bamboo",8)
   for z in (.24,.73,1.23):
    ellipsoid("Woven knot",(x,-.034,z),(.027,.018,.020),"wooddark",1)
  for z in (.24,.73,1.23):rod("Suspension braided cord",(-1.1,-.04,z),(1.1,-.04,z),.013,"cedar")
  rod("Upper rail",(-1.12,0,1.51),(1.12,0,1.51),.045,"wooddark")
 elif i==5:
  revolve("Bamboo airtight tea caddy",[(.3,.04),(.46,.07),(.46,.91),(.41,.98)],"bamboo")
  cyl("Inner tin lid",(0,0,.95),.39,.06,"steel",32)
  cyl("Outer wood-fitted cap",(0,0,1.02),.49,.20,"hinoki",32)
  for z in (.28,.54,.8):hoop("Bamboo growth node",(0,0,z),.462,.023,"bamboodark")
  petals("Carved lid ornament",0,1.13,.13,"cedar",6,y=0)
 elif i==6:
  revolve("Cut bamboo water vessel",[(.26,.03),(.39,.06),(.4,1.12),(.34,1.15),(.28,1.07),(.25,.10)],"bamboo")
  rod("Bamboo projecting pourer",(.32,0,.96),(.89,0,1.12),.12,"bamboo",16)
  hoop("Pourer edge",(.87,0,1.115),.12,.021,"bamboodark",20,"X")
  for z in (.17,.58,1.03):hoop("Visible bamboo joints",(0,0,z),.406,.030,"bamboodark")
 elif i==7:
  rod("Dark lacquered shinobue tube",(-1.17,0,.16),(1.17,0,.16),.088,"bamboo",20)
  for k,x in enumerate([-.72,-.52,-.30,-.09,.13,.33,.54]):
   ellipsoid("Finger hole on flute "+str(k),(x,-.087,.16),(.038,.013,.041),"black",1)
  for k,x in enumerate([-.98,-.87,.73,.82,.96]):
   hoop("Shinobue red cord binding",(x,0,.16),.091,.012,"red",24,"X")
  ellipsoid("Mouth hole",(-1.04,-.09,.16),(.050,.014,.045),"black")
 elif i==8:
  rod("Dragonfly shaft",(0,0,.02),(0,0,1.19),.038,"hinoki")
  for s in (-1,1):
   polygon("Bamboo helicopter tapered wing"+str(s),[(0,0,1.14),(.18*s,0,1.18),(.96*s,0,1.27),(.96*s,0,1.14),(.22*s,0,1.10)],"bamboo",.04)
  hoop("Center rotor binding",(0,0,1.19),.10,.018,"bamboodark")
 elif i==9:
  rod("Long split bamboo broom handle",(0,0,.47),(0,0,1.92),.073,"bamboo",20)
  for j in range(62):
   a=j*math.tau/62
   strand("Rice-straw broom bundle",[(.085*math.cos(a),.085*math.sin(a),.53),
    (.21*math.cos(a),.21*math.sin(a),.31),
    ((.39+.035*(j%3))*math.cos(a),(.39+.035*(j%3))*math.sin(a),.025)],
    "straw" if j%3 else "hinoki",.013,6)
  for z,r in [(.44,.18),(.54,.10)]:hoop("Broom binding rope",(0,0,z),r,.029,"red")
