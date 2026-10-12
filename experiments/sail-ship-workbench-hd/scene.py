"""Render a procedural square-rigged sailing ship in Blender 5.2 Workbench HD."""
from __future__ import annotations
import json
import math
import shutil
import sys
from pathlib import Path
import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from ship import assemble

ID="sail-ship-workbench-hd"
OUT=Path("output52")
FRAMES=OUT/"frames"
FPS=24
FRAME_COUNT=120
WIDTH=1280
HEIGHT=720

def aim(camera,target):
    direction=Vector(target)-camera.location
    camera.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()

def setup():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene=bpy.context.scene
    scene.render.engine="BLENDER_WORKBENCH"
    scene.frame_start=1
    scene.frame_end=FRAME_COUNT
    scene.render.fps=FPS
    scene.render.resolution_x=WIDTH
    scene.render.resolution_y=HEIGHT
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.film_transparent=False

    shading=scene.display.shading
    shading.light="STUDIO"
    shading.color_type="MATERIAL"
    shading.studio_light="paint.sl"
    shading.show_shadows=True
    shading.show_cavity=True
    shading.cavity_type="BOTH"
    shading.curvature_ridge_factor=1.2
    shading.curvature_valley_factor=1.1
    shading.show_specular_highlight=True
    shading.background_type="WORLD"
    scene.world.color=(.26,.40,.58)

    bpy.ops.object.empty_add(type="PLAIN_AXES",location=(0,0,.36))
    rig=bpy.context.object
    rig.name="SAIL SHIP / ANIMATED ASSEMBLY"
    rig.rotation_mode="XYZ"

    bpy.ops.object.camera_add(location=(11,-11,7))
    camera=bpy.context.object
    camera.name="Turntable camera"
    camera.data.lens=34
    aim(camera,(0,0,4.0))
    scene.camera=camera
    return scene,rig,camera

def main():
    OUT.mkdir(exist_ok=True)
    FRAMES.mkdir(parents=True,exist_ok=True)
    scene,rig,camera=setup()
    parts=assemble(rig)
    assert parts["masts"]==3 and parts["sails"]==6
    assert scene.render.engine=="BLENDER_WORKBENCH"
    mesh_count=sum(o.type=="MESH" for o in bpy.data.objects)
    if mesh_count<75:
        raise RuntimeError("Incomplete model: %d mesh objects"%mesh_count)

    stats=[]
    for frame in range(1,FRAME_COUNT+1):
        t=(frame-1)/(FRAME_COUNT-1)
        a=math.tau*t
        scene.frame_set(frame)
        rig.location.z=.36+.06*math.sin(a*2)
        rig.rotation_euler=(math.radians(2.3)*math.sin(a*2+.5),
                            math.radians(1.5)*math.sin(a*1.2),
                            math.radians(3.1)*math.sin(a+.2))
        camera.location=Vector((15.7*math.cos(a),
                                15.7*math.sin(a),
                                6.45+.26*math.sin(a*2)))
        aim(camera,(0,0,4.0))
        bpy.context.view_layer.update()
        scene.render.filepath=str(FRAMES/("frame_%04d.png"%frame))
        bpy.ops.render.render(write_still=True)
        stats.append({"frame":frame,"camera_angle_deg":round(360*t,3),
                      "height":round(rig.location.z,4)})

    shutil.copy2(FRAMES/"frame_0032.png",OUT/"preview.png")
    scene.frame_set(32)
    # Save the authored ship, animation-ready rig and camera in a real .blend.
    rig.keyframe_insert(data_path="location",frame=1)
    rig.keyframe_insert(data_path="rotation_euler",frame=1)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ID+".blend")))

    report={"experiment":ID,
            "blender_version":bpy.app.version_string,
            "engine":scene.render.engine,
            "resolution":[WIDTH,HEIGHT],
            "frame_count":FRAME_COUNT,
            "frame_start":1,"frame_end":FRAME_COUNT,
            "fps":FPS,"duration_seconds":FRAME_COUNT/FPS,
            "preview_frame":32,
            "camera_orbit_degrees":360,
            "component_counts":parts,
            "mesh_object_count":mesh_count,
            "frame_stats":stats}
    (OUT/(ID+"-report.json")).write_text(
        json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("SHIP_REPORT="+json.dumps({k:v for k,v in report.items()
        if k!="frame_stats"},sort_keys=True))

if __name__=="__main__":
    main()
