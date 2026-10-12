"""Procedurally assembled 3-masted sailing ship for Blender 5.2."""
from __future__ import annotations
import math
import bpy
from geometry import material,box,beam,pole,hull,sail,ocean

def assemble(root):
    timber=material("01 Dark varnished hull",(.30,.17,.087))
    lightwood=material("02 Honey teak decks",(.59,.40,.20))
    pale=material("03 Linen sails",(.91,.89,.76))
    mastwood=material("04 Spars and yards",(.41,.26,.12))
    rig=material("05 Hemp rigging",(.32,.27,.17))
    iron=material("06 Aged iron",(.31,.34,.38),.4)
    sea=material("07 Blue sea",(.13,.37,.57))
    foam=material("08 Sea foam",(.91,.94,.98))
    hull(root,timber,lightwood)
    box("Main deck",(0,0,1.82),(5.65,1.72,.12),lightwood,root)
    box("Aft raised deck",(-2.45,0,2.13),(2.32,1.53,.17),lightwood,root)
    box("Forecastle deck",(2.88,0,2.03),(1.15,1.10,.12),lightwood,root)
    box("Stern companion",(-2.18,0,2.45),(.82,.95,.48),timber,root)
    box("Cargo deckhouse",(-.70,0,2.18),(1.25,.95,.42),lightwood,root)
    railposts=0
    for side in (-1,1):
        for x in (-3.45,-2.85,-2.25,-1.65,-1.05,-.45,.15,.75,1.35,1.95,2.55,3.05):
            y=side*1.03*(1-.12*(abs(x)/4.2)**2)
            z=2.12
            beam("Bulwark %s %s"%(side,x),(x,y,z),(x,y,z+.40),.05,lightwood,root)
            railposts+=1
        beam("Guard rail %d"%side,(-3.4,side*.85,2.52),
             (3.2,side*.85,2.48),.072,lightwood,root)

    mast_specs=[("Mizzen",-2.0,5.1),("Main",.15,6.65),("Fore",2.0,5.7)]
    top={}
    for label,x,length in mast_specs:
        pole(label+" mast",(x,0,1.87+length/2),
             .12 if label=="Main" else .095,length,mastwood,root)
        top[label]=(x,0,1.87+length)
        pole(label+" top cap",(x,0,1.87+length),.16,.20,iron,root)
    pole("Bowsprit",(4.36,0,2.52),.075,2.30,mastwood,root,
         (0,math.radians(72),0))

    yard_specs=[
        ("Main course",.15,5.42,3.25,3.05),
        ("Main topsail",.15,7.10,2.40,2.40),
        ("Fore course",2.0,5.05,2.80,2.75),
        ("Fore topsail",2.0,6.38,2.00,2.0),
        ("Mizzen", -2.0,5.15,2.0,2.45),
    ]
    for label,x,z,width,height in yard_specs:
        pole(label+" yard",(x,0,z+height*.46),.053,width,mastwood,root,
             rotation=(math.pi/2,0,0))
        sail(label+" canvas",(x,.04,z),width*.95,height,pale,root,
             fullness=.18+.06*(width/3))
    # Triangular jib near the bowsprit.
    sail("Jib triangular sail",(3.55,0,4.16),2.0,2.65,pale,root,
         fullness=.15,triangle=True)

    # Cables between mastheads, bowsprit and rail, all parented to the hull.
    lines=[
        (top["Main"],top["Fore"]),(top["Main"],top["Mizzen"]),
        (top["Fore"],(5.35,0,3.06)),
        (top["Main"],(5.35,0,3.06)),
        (top["Mizzen"],(-3.70,0,2.18)),
    ]
    for label,x,_ in mast_specs:
        for side in (-1,1):
            lines.append((top[label],(x+.4,side*1.08,2.12)))
            lines.append((top[label],(x-.4,side*1.08,2.12)))
    for i,(a,b) in enumerate(lines):
        beam("Standing rigging %02d"%i,a,b,.021,rig,root)
    for j,(label,x,z,width,height) in enumerate(yard_specs):
        beam("Port yard brace %d"%j,(x,-width*.48,z+height*.46),
             (x-.8,-.98,2.4),.018,rig,root)
        beam("Starboard yard brace %d"%j,(x,width*.48,z+height*.46),
             (x-.8,.98,2.4),.018,rig,root)
    for i,x in enumerate((-3.2,-2.7,-2.2,-1.7,-1.2,-.7,.2,.8,1.4,2.0,2.6)):
        pole("Hull port porthole %02d"%i,(x,-1.07,1.46),.068,.025,iron,root,
             rotation=(math.pi/2,0,0))
        pole("Hull starboard porthole %02d"%i,(x,1.07,1.46),.068,.025,iron,root,
             rotation=(math.pi/2,0,0))
    ocean(sea,foam)
    return {"masts":3,"sails":6,"yards":5,
            "rigging_lines":len(lines)+2*len(yard_specs),
            "rail_posts":railposts,"portholes":22}
