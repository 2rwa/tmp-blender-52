"""Ten writing and document utensils with carved, folded, and decorated details."""
import math
from geometry import *
def make(i):
 if i==0:
  box("Solid carved suzuri inkstone",(0,0,.17),(.91,1.35,.28),"charcoal",.08)
  box("Flat ink grinding land",(0,-.22,.315),(.67,.69,.014),"iron",.035)
  ellipsoid("Recessed wet inkwell",(0,.37,.309),(.28,.22,.013),"black")
  for x in (-.35,.35):
   rod("Carved side relief",(x,-.53,.31),(x,.45,.31),.018,"steel")
  petals("Carved suzuri motif",0,.09,.10,"bronze",5,y=-.69)
 elif i==1:
  rod("Long lacquered brush shaft",(0,0,.39),(0,0,1.72),.062,"cedar",20)
  cyl("Ferrule binding",(0,0,.32),.10,.16,"gold",20)
  cyl("Fine horsehair brush tip",(0,0,.13),.10,.31,"charcoal",24,0)
  for j in range(20):
   a=j*math.tau/20
   rod("Fine tapered brush fiber",(.068*math.cos(a),.068*math.sin(a),.28),
       (0,0,.015),.005,"black",6)
  for z in (1.49,1.53):hoop("Brush maker seal",(0,0,z),.062,.01,"gold")
 elif i==2:
  box("Hand-molded inkstick",(0,0,.15),(.44,1.07,.27),"black",.046)
  box("Gold-colored engraved calligraphy",(0,-.540,.17),(.18,.025,.15),"gold",.003)
  for j in range(5):
   rod("Inkstick gilt border",( -.18+j*.09,-.553,.04),(-.18+j*.09,-.553,.26),.009,"bronze")
  petals("Ink-carved dragon seal",0,.23,.10,"gold",5,y=-.57)
 elif i==3:
  rod("Brass carved paperweight",(-.88,0,.14),(.88,0,.14),.13,"bronze",24)
  for x in (-.70,-.55,0,.55,.7):hoop("Engraved end section",(x,0,.14),.135,.012,"gold",20,"X")
  for x in (-.55,-.25,.25,.55):ellipsoid("Metal inlay", (x,-.13,.14),(.055,.016,.042),"gold")
 elif i==4:
  box("Unrolled makimono rice paper",(0,0,.12),(1.41,1.00,.032),"washi",.012)
  for x in (-.73,.73):rod("Wooden scroll roller",(x,-.6,.12),(x,.60,.12),.085,"cedar",18)
  for j in range(8):
   x=-.47+j*.14
   rod("Calligraphy brushstroke",(x,-.42,.15),(x,-.02,.15),.022,"black")
  for j in range(3):
   x=-.40+j*.43
   ellipsoid("Cinnabar artist seal",(x,.27,.151),(.09,.07,.01),"red")
 elif i==5:
  for j in range(9):
   box("Stack of deckled washi sheets",(j*.009,-j*.006,.08+j*.027),
       (1.15,1.52,.025),"washi",.005)
  for j in range(24):
   x=-.53+(j%8)*.15;y=-.62+(j//8)*.56
   rod("Exposed washi plant fiber",(x,y,.31),(x+.06,y+.04,.31),.006,"hinoki",6)
  hoop("Paper-maker woven seal",(0,-.70,.31),.13,.02,"indigo",18,"Y")
 elif i==6:
  box("Suzuribako black lacquered casket",(0,0,.26),(1.15,.89,.49),"lacquer",.08)
  box("Removable box lid",(0,0,.56),(1.21,.94,.12),"red",.058)
  for x in (-.53,.53):
   box("Fine gold inlaid edge",(x,0,.62),(.022,.92,.018),"gold",.004)
  petals("Large makie motif",-.12,.64,.18,"gold",6,y=-.0)
  for j in range(7):ellipsoid("Constellation of gold dust",(.27+.04*j,.04*(j%2),.63),(.016,.016,.008),"gold",1)
 elif i==7:
  cyl("Carved wood hanko seal", (0,0,.44),.21,.88,"cedar",24)
  cyl("Red ink stamped rubber base",(0,0,.055),.24,.11,"red",24)
  for z in (.14,.22,.72,.83):hoop("Carved seal shaft line",(0,0,z),.213,.014,"wooddark")
  cyl("Inlaid bone crest cap",(0,0,.91),.22,.065,"ivory",24)
  petals("Hanko top emblem",0,.95,.11,"indigo",6,y=-.21)
 elif i==8:
  for j in range(4):
   box("Individual nested inro compartment",(0,0,.20+.24*j),(.67,.46,.22),"lacquer",.068)
   box("Gold division piping",(0,0,.325+.24*j),(.68,.475,.025),"gold",.006)
  strand("Silk inro cord",[(-.32,0,.89),(-.4,0,1.17),(-.12,0,1.46),
    (.25,0,1.47),(.38,0,1.12),(.32,0,.87)],"red",.022)
  ellipsoid("Ivory ojime clasp",(0,0,1.43),(.09,.08,.11),"ivory")
  petals("Makie inro plum crest",0,.62,.12,"gold",6,y=-.248)
 elif i==9:
  box("Kakejiku indigo silk mounting",(0,0,.83),(1.15,.05,1.37),"indigo",.012)
  box("Central washi art scroll",(0,-.032,.81),(.86,.025,1.02),"washi",.008)
  for z in (.08,1.56):
   rod("Scroll mounting roller",(-.70,0,z),(.70,0,z),.055,"cedar")
   for x in (-.73,.73):ellipsoid("Ivory roller end",(x,0,z),(.06,.065,.065),"ivory")
  polygon("Detailed mountain silhouette",[(-.37,-.06,.59),(-.14,-.06,1.09),
   (0,-.06,.85),(.22,-.06,1.16),(.38,-.06,.60)],"celadon")
  ellipsoid("Red artist stamp",(.29,-.086,.42),(.055,.009,.077),"red")
  strand("Hanging cord",[(-.2,0,1.59),(-.18,0,1.84),(0,0,1.95),(.18,0,1.84),(.2,0,1.59)],"gold",.022)
