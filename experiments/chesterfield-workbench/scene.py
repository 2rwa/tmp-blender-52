"""Chesterfield wingback chair — Blender 5.2 Workbench HD orbit render."""
from __future__ import annotations
import json
import math
import shutil
import sys
from pathlib import Path
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chair import build

ID = 'chesterfield-workbench'
OUT = Path('output52')
FRAMES = OUT / 'frames'
WIDTH, HEIGHT = 1280, 720
FIRST, LAST = 1, 96
FPS = 24
PREVIEW = 60


def aim(camera, target):
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z','Y').to_euler()


def setup():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.frame_start, scene.frame_end = FIRST, LAST
    scene.render.fps = FPS
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = False
    sh = scene.display.shading
    sh.light = 'STUDIO'
    sh.color_type = 'MATERIAL'
    sh.show_shadows = True
    sh.show_cavity = True
    sh.cavity_type = 'BOTH'
    sh.show_specular_highlight = True
    sh.background_type = 'WORLD'
    scene.world.color = (.42,.45,.54)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
    chair = bpy.context.object
    chair.name = 'CHESTERFIELD / editable parts / animated root'
    bpy.ops.object.camera_add(location=(-4.6,-4.4,2.6))
    camera = bpy.context.object
    camera.name = 'Workbench HD orbit camera'
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 5.75
    aim(camera, (0,0,1.65))
    scene.camera = camera
    return scene, chair, camera


def main():
    OUT.mkdir(exist_ok=True)
    FRAMES.mkdir(parents=True,exist_ok=True)
    scene, chair, camera = setup()
    counts = build(chair)
    assert counts['tufted_panels'] == 4
    assert counts['wings'] == 2 and counts['bun_feet'] == 4
    if counts['buttons'] < 50:
        raise RuntimeError('Tufting buttons missing')
    frame_stats = []
    target = (0,0,1.70)
    for frame in range(FIRST,LAST+1):
        scene.frame_set(frame)
        t=(frame-FIRST)/(LAST-FIRST)
        angle=math.tau*t
        camera.location = Vector((5.0*math.cos(angle),5.0*math.sin(angle),
                                  2.88+.20*math.sin(angle*2)))
        aim(camera,target)
        # Set actual keyframes so the saved .blend can replay the turntable.
        camera.keyframe_insert(data_path='location',frame=frame)
        camera.keyframe_insert(data_path='rotation_euler',frame=frame)
        bpy.context.view_layer.update()
        scene.render.filepath = str(FRAMES/('frame_%04d.png'%frame))
        bpy.ops.render.render(write_still=True)
        frame_stats.append({'frame':frame,'camera_angle_deg':round(math.degrees(angle),3)})
    shutil.copy2(FRAMES/('frame_%04d.png'%PREVIEW),OUT/'preview.png')
    scene.frame_set(PREVIEW)
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ID+'.blend')))
    report = {
        'experiment':ID,'title':'Chesterfield Wingback Chair — Workbench HD',
        'blender_version':bpy.app.version_string,'engine':scene.render.engine,
        'resolution':[WIDTH,HEIGHT],'frame_count':LAST-FIRST+1,
        'fps':FPS,'preview_frame':PREVIEW,'camera_orbit_degrees':360,
        'mesh_object_count':sum(o.type=='MESH' for o in bpy.data.objects),
        'component_counts':counts,'frame_stats':frame_stats,
    }
    (OUT/(ID+'-report.json')).write_text(
        json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('CHESTERFIELD_RENDER='+json.dumps({k:v for k,v in report.items() if k!='frame_stats'}))


if __name__ == '__main__':
    main()
