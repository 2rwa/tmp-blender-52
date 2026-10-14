"""Five colorful procedural Japanese art assets: independent objects, Workbench turntables."""
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from catalog import CATALOG
import geometry
import runpy
OUT=Path("output52")
FRAMES=144
FPS=24
RES=(500,400)

def clear():
 bpy.ops.object.select_all(action="SELECT")
 bpy.ops.object.delete(use_global=False)
 for blocks in (bpy.data.meshes,bpy.data.materials,bpy.data.cameras,bpy.data.curves):
  for block in list(blocks):
   if block.users==0:blocks.remove(block)
 geometry.init()

def normalize(meshes):
 bpy.context.view_layer.update()
 corners=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
 mins=[min(v[i] for v in corners) for i in range(3)]
 maxs=[max(v[i] for v in corners) for i in range(3)]
 dimensions=[maxs[i]-mins[i] for i in range(3)]
 if max(dimensions)<.01:raise RuntimeError("Degenerate geometry")
 center=((mins[0]+maxs[0])/2,(mins[1]+maxs[1])/2,mins[2])
 scale=1.95/max(dimensions)
 mat=Matrix.Scale(scale,4)@Matrix.Translation(Vector((-center[0],-center[1],-center[2])))
 for o in meshes:o.matrix_world=mat@o.matrix_world
 bpy.context.view_layer.update()
 return dimensions,scale

def render_setup():
 scene=bpy.context.scene
 scene.render.engine="BLENDER_WORKBENCH"
 shade=scene.display.shading
 shade.light="STUDIO"
 shade.color_type="MATERIAL"
 shade.show_shadows=True
 shade.show_cavity=True
 shade.cavity_type="BOTH"
 shade.background_type="VIEWPORT"
 shade.background_color=(.025,.041,.065)
 scene.render.resolution_x,scene.render.resolution_y=RES
 scene.render.resolution_percentage=100
 scene.render.fps=FPS
 scene.render.image_settings.file_format="PNG"
 scene.render.film_transparent=False
 scene.frame_start=1;scene.frame_end=FRAMES
 scene.view_settings.view_transform="Standard"
 bpy.ops.object.camera_add(location=(3.2,-4.3,2.8))
 cam=bpy.context.object
 cam.name="Turntable_orbit_camera"
 cam.data.type="ORTHO"
 cam.data.ortho_scale=3.0
 scene.camera=cam
 return scene,cam

def look(cam,angle):
 target=Vector((0,0,.85))
 cam.location=(5.0*math.cos(angle),5.0*math.sin(angle),3.0)
 cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()

def render(item,batch):
 ident,japanese,category,index=item
 folder=OUT/"items"/ident
 folder.mkdir(parents=True,exist_ok=True)
 tmp=OUT/"frames"/ident
 tmp.mkdir(parents=True,exist_ok=True)
 clear()
 source=HERE/"generated"/(ident+".py")
 if not source.is_file():raise RuntimeError("Missing Gemini-generated module: "+ident)
 builder=runpy.run_path(str(source)).get("build_model")
 if not callable(builder):raise RuntimeError("No build_model(): "+ident)
 builder()
 meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
 # Workbench MATERIAL mode uses Material.diffuse_color, not Principled Base Color.
 # Enforce the *model's* materials, not the reference palette loaded by geometry.init().
 model_mats={m.name:m for o in meshes for m in o.data.materials if m}
 if len(model_mats)<3:raise RuntimeError("COLOR_GATE: insufficient assigned materials")
 colors=[]
 for m in model_mats.values():
  if not m.use_nodes:raise RuntimeError("COLOR_GATE: node material required: "+m.name)
  node=m.node_tree.nodes.get("Principled BSDF")
  if node is None or "Base Color" not in node.inputs:raise RuntimeError("COLOR_GATE: missing Principled color: "+m.name)
  c=tuple(float(x) for x in m.diffuse_color)
  base=tuple(float(x) for x in node.inputs["Base Color"].default_value)
  if max(abs(c[i]-base[i]) for i in range(4))>.035:raise RuntimeError("COLOR_GATE: diffuse_color and BSDF differ: "+m.name)
  colors.append(c)
 if max(max(abs(a[i]-b[i]) for i in range(3)) for a in colors for b in colors)<.18:
  raise RuntimeError("COLOR_GATE: not enough differentiated colors")
 if not any(max(c[:3])-min(c[:3])>.13 for c in colors):
  raise RuntimeError("COLOR_GATE: no visible chromatic palette")
 print("WORKBENCH_COLOR_GATE",ident,"materials",len(model_mats),flush=True)

 if len(meshes)<2:raise RuntimeError(f"Missing assembled parts for {ident}")
 dimensions,factor=normalize(meshes)
 poly=sum(len(o.data.polygons) for o in meshes)
 if poly<150:raise RuntimeError(f"Geometry suspiciously primitive: {ident}, faces={poly}")
 for o in bpy.context.selected_objects:o.select_set(False)
 for o in meshes:o.select_set(True)
 bpy.context.view_layer.objects.active=meshes[0]
 bpy.ops.export_scene.gltf(filepath=str(folder/(ident+".glb")),
  export_format="GLB",use_selection=True)
 for o in meshes:o.select_set(False)
 scene,cam=render_setup()
 look(cam,-math.pi/2)
 scene.frame_set(1)
 bpy.ops.wm.save_as_mainfile(filepath=str(folder/(ident+".blend")))
 for frame in range(1,FRAMES+1):
  scene.frame_set(frame)
  look(cam,-math.pi/2+math.tau*(frame-1)/FRAMES)
  scene.render.filepath=str(tmp/f"frame_{frame:04d}.png")
  bpy.ops.render.render(write_still=True)
 picker=("import sys;from PIL import Image,ImageStat;"
  "scores=[(float(ImageStat.Stat(Image.open(p).convert('L')).stddev[0]),"
  "int(p.rsplit('_',1)[-1].split('.')[0])) for p in sys.argv[1:]];"
  "print(*max(scores))")
 candidates=[str(tmp/f"frame_{f:04d}.png") for f in (1,19,37,55,73,91,109,127)]
 scoretext=subprocess.check_output(["python3","-c",picker,*candidates],text=True).strip()
 contrast,chosen=scoretext.split()
 contrast=float(contrast);chosen=int(chosen)
 shutil.copy2(tmp/f"frame_{chosen:04d}.png",folder/"preview.png")
 subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
  "-framerate",str(FPS),"-start_number","1",
  "-i",str(tmp/"frame_%04d.png"),
  "-c:v","libx264","-preset","veryfast","-crf","26",
  "-pix_fmt","yuv420p","-movflags","+faststart",
  str(folder/"turntable.mp4")],check=True)
 shutil.rmtree(tmp)
 metadata={
  "id":ident,"title":japanese,"category":category,"variant":index,
  "generator":"japanese-festival-flash38-color-5","detail_level":"gemini_flash38_workbench_color_v2",
  "blender_version":bpy.app.version_string,
  "engine":scene.render.engine,
  "mesh_objects":len(meshes),"polygons":poly,
  "materials":len(set(m.name for o in meshes for m in o.data.materials if m)),
  "dimensions_original":dimensions,"normalization_scale":factor,
  "frame_count":FRAMES,"fps":FPS,"resolution":list(RES),
  "preview_frame":chosen,"preview_stddev":round(contrast,2),"batch":batch}
 (folder/"metadata.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("REBUILT_ASSET",ident,"faces",poly,"parts",len(meshes),"preview",chosen,flush=True)
 return metadata

def main():
 args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
 batch=int(args[args.index("--batch")+1]) if "--batch" in args else 0
 if batch!=0:raise RuntimeError("batch must be 0")
 (OUT/"frames").mkdir(parents=True,exist_ok=True)
 summary=[render(x,batch) for x in CATALOG]
 assert len(summary)==5
 (OUT/"batch.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
