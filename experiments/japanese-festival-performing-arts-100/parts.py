"""Reusable festival geometry. Distinct sculptural pieces; no external dependencies."""
import math
from geometry import *
T=math.tau
def gridbeams(prefix,w,d,z,col="cedar",n=7):
 for k in range(n):
  x=-w/2+w*k/(n-1)
  box(prefix+" plank", (x,0,z),(.045,d,.045),col,.008)
 for s in (-1,1):
  box(prefix+" sill",(0,s*d*.50,z), (w,.06,.09),"wooddark")
def pole(name,height=1.7,color="cedar",x=0,y=0,r=.052):
 cyl(name,(x,y,height/2),r,height,color,16)
 for z in (.13,height*.42,height*.84):hoop(name+" binding",(x,y,z),r+.007,.012,"gold",16)
def flower(name,pos,r=.15,petal="gold",n=7):
 x,y,z=pos
 for i in range(n):
  a=T*i/n
  ellipsoid(name+" petal",(x+r*math.cos(a),y,z+r*math.sin(a)),(.08,.035,.11),petal,2)
 ellipsoid(name+" center",(x,y-.05,z),(.06,.05,.065),"red")
def fringe(name,x,y,z,width=.7,count=14,color="gold"):
 for j in range(count):
  xx=x-width*.5+width*j/(count-1)
  strand(name+str(j),[(xx,y,z),(xx+.01,y,z-.16),(xx-.02,y,z-.27)],color,.012)
def lantern(name,x=0,y=0,z=1.3,scale=1,col="red"):
 def P(v):return v*scale
 cyl(name+" thin top",(x,y,z+P(.37)),P(.21),P(.07),"wooddark",24)
 for k in range(9):
  h=(k-4)*P(.071)
  rad=P(.17+.11*math.sqrt(max(0,1-((k-4)/4.7)**2)))
  cyl(name+" folded paper",(x,y,z+h),rad,P(.073),col,24)
  hoop(name+" bamboo rung",(x,y,z+h),rad,P(.009),"gold",24)
 cyl(name+" bottom",(x,y,z-P(.35)),P(.20),P(.07),"wooddark",24)
 ellipsoid(name+" painted crest",(x,y-P(.274),z),(.09*scale,.025*scale,.14*scale),"washi",2)
 strand(name+" hanging cord",[(x,y,z+P(.4)),(x,y,z+P(.64))],"cedar",P(.016))
 fringe(name+" tassel",x,y,z-P(.39),P(.17),7,"gold")
def roof(name,z=1.2,w=1.3,d=1.0,rise=.43,col="wooddark",tiers=1):
 for tier in range(tiers):
  zw=z+tier*.35;ww=w*(1-.13*tier);dd=d*(1-.13*tier)
  box(name+" underedge",(0,0,zw),(ww*1.17,dd*1.20,.09),"gold")
  for sign in (-1,1):
   v=[(-ww*.62,-dd*.63,zw), (ww*.62,-dd*.63,zw),
      (ww*.43,0,zw+rise),(-ww*.43,0,zw+rise)] if sign==-1 else [
      (-ww*.43,0,zw+rise),(ww*.43,0,zw+rise),
      (ww*.62,dd*.63,zw),( -ww*.62,dd*.63,zw)]
   # Face as shallow solid quadrilateral in 3D
   mesh(name+" hipped roof",v,[(0,1,2,3)],col)
  for j in range(20):
   x=-ww*.6+ww*1.2*j/19
   for sign in (-1,1):
    strand(name+" tile rib",[(x,0,zw+rise),(x,sign*dd*.63,zw)],"charcoal",.014)
  rod(name+" ridge",(-ww*.43,0,zw+rise),(ww*.43,0,zw+rise),.048,"gold")
  for sign in (-1,1):
   ellipsoid(name+" decorative ridge finial",(sign*ww*.44,0,zw+rise),(.07,.10,.07),"gold",2)
def bird(name,z=1.86,x=0):
 ellipsoid(name+" torso",(x,0,z),(.19,.11,.16),"gold")
 ellipsoid(name+" head",(x-.13,0,z+.20),(.12,.09,.13),"gold")
 for s in (-1,1):
  polygon(name+" phoenix wing",[(x-.07,s*.12,z+.03),(x+.11,s*.15,z+.46),(x+.37,s*.15,z+.27),(x+.15,s*.14,z+.15)],"gold",.10)
 for j in range(7):
  strand(name+" trailing tail",[(x+.16,0,z),(x+.3+j*.025,0,z+.11),(x+.49+j*.05,0,z-.19)],"gold",.016)
 cyl(name+" beak",(x-.26,0,z+.2),.045,.10,"vermilion",8,0).rotation_euler.y=math.pi/2
def wheel(name,x,y,z=.30,R=.28,spokes=14):
 hoop(name+" outer tire",(x,y,z),R,.057,"wooddark",40,"Y")
 hoop(name+" gold hoop",(x,y,z),R*.87,.017,"gold",40,"Y")
 cyl(name+" axle hub",(x,y,z),.09,.17,"bronze",24).rotation_euler.x=math.pi/2
 for k in range(spokes):
  a=T*k/spokes
  rod(name+" spoke",(x,y,z),(x+R*math.cos(a),y,z+R*math.sin(a)),.025,"hinoki",8)
 for k in range(spokes): # exposed rivets
  a=T*k/spokes
  ellipsoid(name+" tire nail",(x+R*math.cos(a),y-.055,z+R*math.sin(a)),(.015,.015,.016),"gold",1)
def flag(name,x,z,color="red"):
 polygon(name+" hanging banner",[(x,-.08,z),(x+.47,-.08,z-.08),(x+.42,-.08,z-.78),(x-.02,-.08,z-.72)],color,.025)
 flower(name+" emblem",(x+.21,-.11,z-.43),.095,"gold")
 fringe(name+" banner fringe",x+.2,-.08,z-.70,.35,11)
def float_model(kind=0):
 """Large structural builds, approximately 1000+ parts with visible differences."""
 wheeled=kind not in (0,1,6,7,8)
 big=(kind in (2,3,4,5,6,7))
 w=1.6 if big else 1.23;d=1.16 if big else .94
 box("Heavy joined lacquered chassis",(0,0,.56),(w,d,.21),"wooddark",.04)
 for x in (-w*.42,w*.42):
  for y in (-d*.41,d*.41):
   box("Through-tenon oak support",(x,y,.32),(.16,.15,.48),"cedar",.02)
 for s in (-1,1):
  box("Side carrying beam",(0,s*d*.30,.31),(w*1.60,.13,.12),"hinoki")
  for j in range(8):
   x=-w*.72+j*w*1.44/7
   hoop("Beam metal band",(x,s*d*.30,.31),.066,.012,"gold",12,"X")
 if wheeled:
  for x in (-w*.39,w*.39):
   for s in (-1,1):wheel("Carved float wheel",x,s*d*.64,.29,.31 if big else .27)
 if kind==9:
  for x in (-.42,.42):
   for y in (-.22,.22):wheel("Massive demonstration wheel",x,y,.62,.57,24)
 for s in (-1,1):
  for t in (-1,1):
   x=s*w*.38;y=t*d*.36
   box("Turned festival pillar",(x,y,.96),(.08,.08,.7),"vermilion")
   for zz in (.65,1.06,1.32):ellipsoid("Brass pillar fitting",(x,y,zz),(.10,.10,.045),"gold")
 for z in (.70,1.24):
  for y in (-d*.43,d*.43):
   box("Carved balustrade",(0,y,z),(w*.96,.065,.06),"gold")
  for x in (-w*.44,w*.44):
   box("Hand-carved transverse sill",(x,0,z),(.06,d*.92,.06),"gold")
 for j in range(18):
  x=-w*.42+j*w*.84/17
  for s in (-1,1):rod("Miniature carved railing baluster",(x,s*d*.43,.75),(x,s*d*.43,1.22),.025,"hinoki",8)
 if kind in (0,1,2,3,4,5,6):
  roof("Festival shrine multi-tier roofing",1.44,w*1.12,d*1.08,.44,"lacquer",2 if big else 1)
  if kind in (1,2,5):bird("Roof gilded phoenix",2.27,0)
  elif kind==0:bird("Shrine roof phoenix",1.95,0)
 else:
  box("Tall festival altar platform",(0,0,1.42),(w*.85,d*.87,.15),"red")
 if kind==5: # tall hoko pole
  pole("Tall hoko festival mast",3.8,"gold",0,0,.09)
  for z in (2.24,2.75,3.16):flag("Hoko signal banner",-.4,z,"red")
  ellipsoid("Golden hoko standard",(0,0,3.83),(.22,.22,.29),"gold")
 elif kind==6:
  drum("Taikodai enormous drum",(0,0,1.72),1.02,.48,axis="Y")
 elif kind==7:
  pole("Kasaboko central pole",3.0,"cedar")
  for j in range(14):
   a=T*j/14
   strand("Silk parasol cover",[(0,0,3.03),(.7*math.cos(a),.7*math.sin(a),2.54)],"red",.040)
  for k in range(10):lantern("Kasaboko lantern",.66*math.cos(T*k/10),.66*math.sin(T*k/10),1.75,.45)
 elif kind==8:
  for j in range(5):
   z=1.46+j*.42
   for s in (-1,1):lantern("Tiered lantern tower",s*.34,0,z,.39)
 else:
  for x in (-w*.29,w*.29):
   for y in (-d*.45,d*.45):lantern("Hanging lantern",x,y,1.14,.43)
  for x in (-w*.19,w*.19):flag("Shrine embroidered banner",x,1.46,"indigo")
def drum(name,pos=(0,0,.76),R=.58,L=.80,axis="Y",col="red",tension=True):
 x,y,z=pos
 ob=cyl(name+" hardwood shell",pos,R,L,col,40)
 if axis=="Y":ob.rotation_euler.x=math.pi/2
 if axis=="X":ob.rotation_euler.y=math.pi/2
 for s in (-1,1):
  off=L*.5*s
  cap=(x,y+off,z) if axis=="Y" else ((x+off,y,z) if axis=="X" else (x,y,z+off))
  skin=cyl(name+" taut drum skin",cap,R*1.03,.052,"ivory",40)
  if axis=="Y":skin.rotation_euler.x=math.pi/2
  if axis=="X":skin.rotation_euler.y=math.pi/2
  hoop(name+" leather head rim",cap,R*1.02,.040,"wooddark",40,axis)
  for k in range(24):
   a=T*k/24
   if axis=="Y":p=(x+R*math.cos(a),y+off*1.08,z+R*math.sin(a))
   else:p=(x+R*math.cos(a),y+R*math.sin(a),z+off*1.08)
   ellipsoid(name+" bronze nail",p,(.030,.02,.03),"gold",1)
 if tension:
  for k in range(22):
   a=T*k/22
   strand(name+" tightening rope",[(x+R*math.cos(a),y-L*.52,z+R*math.sin(a)),
      (x+(R+.045)*math.cos(a+.15),y,z+(R+.045)*math.sin(a+.15)),
      (x+R*math.cos(a+.3),y+L*.52,z+R*math.sin(a+.3))],"straw",.014)
 for k in range(12):
  a=T*k/12
  rod(name+" wood grain",(x+(R+.008)*math.cos(a),y-L*.41,z+(R+.008)*math.sin(a)),
      (x+(R+.008)*math.cos(a),y+L*.41,z+(R+.008)*math.sin(a)),.010,"wooddark")
def mask(name="Hand-carved stage mask",style=0,color="ivory"):
 ellipsoid(name+" substantial face blank",(0,0,1.08),(.47,.22,.66),color,3)
 ellipsoid(name+" sculpted forehead",(0,-.20,1.36),(.37,.12,.29),color)
 ellipsoid(name+" nose bridge",(0,-.32,1.09),(.12,.15,.24),color)
 ellipsoid(name+" nasal tip",(0,-.45,.96),(.16,.12,.10),color)
 ellipsoid(name+" chin",(0,-.24,.69),(.29,.16,.15),color)
 for s in (-1,1):
  ellipsoid(name+" hollow eye",(.20*s,-.40,1.23),(.12,.043,.068),"black")
  ellipsoid(name+" raised eyebrow",(.20*s,-.34,1.36),(.18,.06,.048),"wooddark" if style!=1 else "red")
  ellipsoid(name+" carved cheek",(.26*s,-.28,.96),(.20,.09,.15),color)
  hoop(name+" ear hook",(.43*s,0,1.13),.07,.025,"gold",16,"X")
 ellipsoid(name+" dark mouth",(0,-.35,.80),(.22,.045,.07),"black")
 if style in (1,3,4,5):
  for s in (-1,1):
   rod(name+" curving oni horn",(.23*s,-.10,1.59),(.38*s,-.08,2.05),.095,"gold" if style==3 else "ivory",12,0)
   rod(name+" angry cheek ink",(.26*s,-.41,1.19),(.34*s,-.34,.82),.038,"red",8)
 if style==2:
  rod(name+" long tengu nose",(0,-.45,1.07),(0,-1.08,1.13),.12,"vermilion",16)
 if style==4:
  for s in (-1,1):polygon(name+" fox pointy ear",[(.2*s,0,1.49),(.4*s,0,1.88),(.46*s,0,1.48)],color,.10)
 if style==5:
  for j in range(10):
   x=-.31+j*.07
   box(name+" fearsome teeth",(x,-.41,.8),(.05,.045,.075),"ivory",.004)
 if style==0:flower(name+" delicate painted cheek",(.22,-.42,.96),.075,"pink",5)
def fan(name="Festival folding fan",N=26,color="red"):
 angle=math.pi*.83
 for j in range(N):
  a=-angle/2+j*angle/N;b=-angle/2+(j+1)*angle/N
  polygon(name+" gold-threaded paper pleat",[
    (.16*math.sin(a),-.02,.18+.16*math.cos(a)),
    (1.25*math.sin(a),-.02,.18+1.25*math.cos(a)),
    (1.25*math.sin(b),-.02,.18+1.25*math.cos(b)),
    (.16*math.sin(b),-.02,.18+.16*math.cos(b))],color if j%4 else "gold",.014)
  rod(name+" carved fan bone",(0,-.025,.18),
      (1.26*math.sin(a),-.035,.18+1.26*math.cos(a)),.012,"cedar",8)
 ellipsoid(name+" pivot rivet",(0,-.07,.18),(.065,.034,.07),"gold")
 for j in range(7):
  a=-angle/2+(j+.5)*angle/7
  flower(name+" decoration",(.91*math.sin(a),-.05,.18+.91*math.cos(a)),.04,"ivory",5)
def costume(name="Costume",color="red",pattern="gold"):
 polygon(name+" left ample sleeve",[(-.24,0,1.42),(-1.03,0,1.29),(-1.0,0,.36),(-.34,0,.48)],color,.09)
 polygon(name+" right ample sleeve",[(.24,0,1.42),(1.03,0,1.29),(1.0,0,.36),(.34,0,.48)],color,.09)
 box(name+" long body",(0,0,.87),(.67,.23,1.35),color,.08)
 for x in (-.17,.17):
  strand(name+" crossed ivory collars",[(x*.8,-.14,1.51),(0,-.16,1.25),
       (-x*1.7,-.16,.98)],"ivory",.04)
 box(name+" decorative sash",(0,-.14,.79),(.77,.08,.19),pattern)
 ellipsoid(name+" central ornate knot",(0,-.22,.79),(.15,.065,.12),"gold")
 for s in (-1,1):
  fringe(name+" sleeve tassel",s*.67,-.04,.43,.53,12,pattern)
  for j in range(4):
   z=.32+j*.22
   flower(name+" embroidered chrysanthemum",(.55*s,-.13,z),.067,pattern,5)
 for j in range(6):
  z=.25+j*.13
  rod(name+" brocade lower pattern",(-.24,-.13,z),(.24,-.13,z),.007,pattern)
def shrine_gate(name="Torii",span=1.7,height=2.1):
 for s in (-1,1):
  pole(name+" lacquered main pillar",height,"vermilion",s*span*.39,0,.10)
  box(name+" black foot",(s*span*.39,0,.07),(.26,.26,.13),"wooddark")
 box(name+" kasagi upper crossbeam",(0,0,height+.04),(span*1.14,.24,.18),"wooddark",.024)
 box(name+" nuki secondary beam",(0,0,height*.71),(span*.93,.12,.11),"vermilion")
 for s in (-1,1):ellipsoid(name+" finial gold", (s*span*.53,0,height+.12),(.09,.16,.09),"gold")
 box(name+" traditional central plate",(0,-.14,height*.82),(.26,.05,.22),"gold")
