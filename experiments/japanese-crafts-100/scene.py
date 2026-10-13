"""Build ten separate Japanese low-poly craft assets per matrix shard."""
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from catalog import CATALOG
import geometry
import model_tea,model_kitchen,model_bamboo,model_home,model_wear
import model_writing,model_folk,model_ritual,model_woodwork,model_craft
MAKERS=dict(zip(("tea","kitchen","bamboo","home","wear","writing","folk","ritual","woodwork","craft"),
 (model_tea,model_kitchen,model_bamboo,model_home,model_wear,model_writing,model_folk,model_ritual,model_woodwork,model_craft)))
ROOT=Path("output52")
FPS=24
FRAMES=144
SIZE=(400,300)

def reset():
 bpy.ops.object.select_all(action="SELECT")
 bpy.ops.object.delete(use_global=False)
 for collection in (bpy.data.meshes,bpy.data.materials,bpy.data.cameras,bpy.data.curves):
  for block in list(collection):
   if block.users==0:collection.remove(block)
 geometry.init()

def fit(meshes):
 corners=[]
 for ob in meshes:
  for c in ob.bound_box:corners.append(ob.matrix_world@Vector(c))
 low=[min(p[i] for p in corners) for i in range(3)]
 high=[max(p[i] for p in corners) for i in range(3)]
 span=[high[i]-low[i] for i in range(3)]
 factor=1.70/max(max(span),.01)
 center=((low[0]+high[0])*.5,(low[1]+high[1])*.5,low[2])
 transform=Matrix.Scale(factor,4)@Matrix.Translation(Vector((-center[0],-center[1],-center[2])))
 for ob in meshes:ob.matrix_world=transform@ob.matrix_world
 return factor,span

def setup_render():
 sc=bpy.context.scene
 sc.render.engine="BLENDER_WORKBENCH"
 sc.display.shading.light="STUDIO"
 sc.display.shading.color_type="MATERIAL"
 sc.display.shading.show_shadows=True
 sc.display.shading.show_cavity=True
 sc.display.shading.cavity_type="BOTH"
 sc.display.shading.background_type="VIEWPORT"
 sc.display.shading.background_color=(0.035,0.055,0.080)
 sc.render.film_transparent=False
 sc.render.resolution_x,sc.render.resolution_y=SIZE
 sc.render.resolution_percentage=100
 sc.render.fps=FPS
 sc.render.image_settings.file_format="PNG"
 sc.frame_start=1;sc.frame_end=FRAMES
 bpy.ops.object.camera_add(location=(3.2,-4.3,2.8))
 cam=bpy.context.object
 cam.name="Turntable_Camera"
 cam.data.type="ORTHO";cam.data.ortho_scale=3.6;sc.camera=cam
 return sc,cam

def aim(cam,angle):
 target=Vector((0,0,.83))
 cam.location=(4.6*math.cos(angle),4.6*math.sin(angle),3.2)
 cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()

def generate(item,shard):
 ident,japanese,group,variant=item
 folder=ROOT/"items"/ident
 folder.mkdir(parents=True,exist_ok=True)
 temp=ROOT/"frames"/ident
 temp.mkdir(parents=True,exist_ok=True)
 reset()
 MAKERS[group].make(variant)
 meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
 if not meshes:raise RuntimeError(f"empty geometry: {ident}")
 scale,span=fit(meshes)
 for o in bpy.context.selected_objects:o.select_set(False)
 for o in meshes:o.select_set(True)
 bpy.context.view_layer.objects.active=meshes[0]
 bpy.ops.export_scene.gltf(filepath=str(folder/(ident+".glb")),export_format="GLB",use_selection=True)
 sc,cam=setup_render()
 aim(cam,0)
 bpy.ops.wm.save_as_mainfile(filepath=str(folder/(ident+".blend")))
 for frame in range(1,FRAMES+1):
  sc.frame_set(frame)
  aim(cam,math.tau*(frame-1)/FRAMES)
  sc.render.filepath=str(temp/f"frame_{frame:04d}.png")
  bpy.ops.render.render(write_still=True)
 shutil.copy2(temp/"frame_0001.png",folder/"preview.png")
 subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
  "-framerate",str(FPS),"-start_number","1","-i",str(temp/"frame_%04d.png"),
  "-c:v","libx264","-preset","veryfast","-crf","29","-pix_fmt","yuv420p",
  "-movflags","+faststart",str(folder/"turntable.mp4")],check=True)
 shutil.rmtree(temp)
 metadata={"id":ident,"title":japanese,"category":group,"variant":variant,
  "blender_version":bpy.app.version_string,"engine":sc.render.engine,
  "resolution":list(SIZE),"fps":FPS,"frames":FRAMES,
  "mesh_objects":len(meshes),"polygons":sum(len(o.data.polygons) for o in meshes),
  "initial_dimensions":span,"fit_scale":scale,"shard":shard}
 (folder/"metadata.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("CRAFT_COMPLETED",ident,metadata["polygons"],flush=True)
 return metadata

def main():
 args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
 shard=int(args[args.index("--batch")+1]) if "--batch" in args else 0
 if shard not in range(10):raise ValueError("batch must be 0..9")
 ROOT.mkdir(parents=True,exist_ok=True)
 (ROOT/"frames").mkdir(exist_ok=True)
 rows=[generate(row,shard) for row in CATALOG[shard*10:shard*10+10]]
 (ROOT/"batch.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 assert len(rows)==10
if __name__=="__main__":main()
