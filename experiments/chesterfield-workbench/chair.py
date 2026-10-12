"""Chesterfield wingback chair: deep button tufting, leather scrolls, studs, timber feet."""
import math
import bpy
from geometry import material, cuboid, cylinder, ball, tube
from upholstery import tufted


def build(root):
    leather = material('01 Burgundy oxblood leather', (.27, .067, .059))
    edge = material('02 Dark sewn leather welt', (.135, .042, .032))
    warm = material('03 Brighter raised leather', (.33, .085, .071))
    gold = material('04 Burnished upholstery studs', (.64, .48, .23), .72)
    buttons = material('05 Covered leather buttons', (.13, .042, .039))
    wood = material('06 Turned walnut feet', (.35, .18, .085))
    ground = material('07 Photography plinth', (.50, .55, .61))
    backcloth = material('08 Studio cyclorama', (.30, .36, .46))

    cuboid('Studio ground', (0, 0, -.085), (7.5, 7.5, .15), ground, None, .03)
    cuboid('Studio backdrop', (0, 3.20, 2.4), (7.5, .10, 4.8), backcloth, None, 0)

    # Structure, all parented as editable individual objects under a single rig.
    cuboid('Internal seat frame', (0, -.07, .91), (1.95, 1.42, .40), leather, root, .19)
    cuboid('Under-seat padded apron', (0, -.08, .82), (1.90, 1.38, .22), edge, root, .07)
    cuboid('Tall curved back upholstery', (0, .56, 2.08), (1.90, .32, 2.33), leather, root, .17)

    # Seat surface and upright back each have actual high-resolution displacement.
    count_buttons = count_seams = 0
    def quilt(name, w, h, cols, rows, pos, rot=(0,0,0), relief=.13):
        nonlocal count_buttons, count_seams
        ob, nb, ns = tufted(name, w, h, cols, rows, pos, rot,
                            warm, buttons, edge, root, relief)
        count_buttons += nb
        count_seams += ns
        return ob
    quilt('Seat diamond-tufted cushion', 1.60, 1.12, 5, 4,
          (0, -.13, 1.23), relief=.13)
    quilt('Backrest diamond-tufted leather', 1.60, 1.96, 5, 7,
          (0, .355, 2.12), (math.pi/2, 0, 0), .145)

    # Each padded arm slopes slightly down towards the rounded front scroll.
    for side, name in [(-1,'Left'), (1,'Right')]:
        x=side * 1.03
        cuboid(name+' outer leather arm', (x, -.14, 1.45),
               (.40, 1.70, .70), leather, root, .15)
        cuboid(name+' inner arm pad', (side*.855,-.13,1.50),
               (.16,1.34,.48), warm, root, .065)
        quilt(name+' arm inset diamond leather', 1.22, .41, 4, 2,
              (side*.819, -.12, 1.60),
              (math.pi/2, 0, side * math.pi/2), .065)
        # Rolled arms are solid cylindrical leather volumes with end-scroll.
        cylinder(name+' cylindrical arm scroll', (x, -.21, 1.82),
                 .205, 1.48, leather, root, (math.pi/2,0,0), 40)
        ball(name+' front arm scroll bulb', (x,-.97,1.82),
             (.255,.215,.240), leather, root)
        ball(name+' front scroll center button', (x,-1.165,1.82),
             (.058,.014,.058), buttons, root)
        # Wingback ears spread slightly wider at the top.
        verts = [
            (side*.78,.53,1.94),(side*1.15,.40,2.10),
            (side*1.29,.25,3.17),(side*.80,.56,3.34),
            (side*.82,.72,1.94),(side*1.22,.62,2.10),
            (side*1.36,.48,3.17),(side*.83,.75,3.34),
        ]
        faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),
               (2,6,7,3),(3,7,4,0)]
        mesh=bpy.data.meshes.new(name+' wing mesh')
        mesh.from_pydata(verts,[],faces); mesh.update()
        wing=bpy.data.objects.new(name+' sculpted wingback',mesh)
        bpy.context.collection.objects.link(wing)
        wing.parent=root
        wing.data.materials.append(leather)
        bev=wing.modifiers.new('Soft thick leather edges','BEVEL')
        bev.width=.085; bev.segments=3
        wing.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
        # Antique brass nailheads along the leading edges of wing and arms.
        for i in range(17):
            t=i/16
            z=2.08+t*1.08
            bx=side*(1.15+.14*t)
            by=.39-.14*t
            ball(name+' wing nail %02d'%i,(bx,by-.028,z),
                 (.026,.026,.026),gold,root,12)
        for i in range(13):
            t=i/12
            ball(name+' scroll nail %02d'%i,
                 (side*1.225,-.99+1.45*t,1.64),
                 (.026,.026,.026),gold,root,12)
        # Rolled piping follows the top of the arm to the back.
        tube(name+' leather top piping',
             [(x,-.96+k*1.45/12,2.021) for k in range(13)],
             .015,edge,root)

    # Chesterfield-style nailheads across the underside of the seat.
    for i in range(21):
        x=-.89+1.78*i/20
        ball('Front apron brass nail %02d'%i,
             (x,-.817,.93),(.025,.025,.025),gold,root,12)
    for side in (-1,1):
        for y in (-.65,.62):
            # Rounded, turned walnut bun feet (not simple rectangular blocks).
            x=side*.76
            cylinder('Foot plinth %s %s'%(side,y),(x,y,.25),.125,.16,wood,root)
            ball('Turned wooden bun %s %s'%(side,y),(x,y,.155),
                 (.16,.16,.115),wood,root)
            cylinder('Foot toe cap %s %s'%(side,y),(x,y,.07),
                     .092,.055,wood,root)

    counts={
        'tufted_panels':4,'buttons':count_buttons,'diamond_seams':count_seams,
        'wings':2,'arm_scrolls':2,'bun_feet':4,'nailheads':81,
        'mesh_objects':sum(o.type=='MESH' for o in bpy.data.objects),
    }
    return counts
