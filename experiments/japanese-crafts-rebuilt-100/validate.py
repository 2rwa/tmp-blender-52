"""Check every published Blender/GLB/video/png and inspect real image contrast."""
import json
import subprocess
import sys
from pathlib import Path
from PIL import Image,ImageStat,ImageChops
sys.path.insert(0,str(Path(__file__).resolve().parent))
from catalog import CATALOG
OUT=Path("output52")
EXPECTED=(500,400)
def validate_silhouette(bbox, colored_pixels):
 """Aspect-ratio-aware test: long thin tools must remain visible, not fill both axes.
 Synthetic mask regression cases live in test_validation.py.
 """
 if bbox is None:raise AssertionError("Completely blank preview")
 w,h=bbox[2]-bbox[0],bbox[3]-bbox[1]
 if max(w,h)<110:raise AssertionError(f"Too small on screen: {w}x{h}")
 if min(w,h)<12:raise AssertionError(f"Edge-on/near-invisible preview: {w}x{h}")
 if colored_pixels<350:raise AssertionError(f"Insufficient visible surface: {colored_pixels} px")
 return w,h

def check(row):
 ident,title,category,_=row
 folder=OUT/"items"/ident
 files={"preview.png":2500,"turntable.mp4":4000,ident+".blend":1800,
        ident+".glb":700,"metadata.json":250}
 for filename,n in files.items():
  p=folder/filename
  if not p.is_file() or p.stat().st_size<n:raise AssertionError(f"Missing/small {p}")
 with (folder/(ident+".glb")).open("rb") as f:
  if f.read(4)!=b"glTF":raise AssertionError("Malformed GLB "+ident)
 with (folder/(ident+".blend")).open("rb") as f:
  b=f.read(8)
  if not (b.startswith(b"BL") or b.startswith(b"\x1f\x8b") or b.startswith(b"\x28\xb5")):
   raise AssertionError("Malformed .blend "+ident)
 meta=json.loads((folder/"metadata.json").read_text(encoding="utf8"))
 for k,v in [("id",ident),("title",title),("category",category),("generator","japanese-crafts-rebuilt-100"),
             ("frame_count",144),("fps",24),("resolution",[500,400]),("engine","BLENDER_WORKBENCH")]:
  if meta.get(k)!=v:raise AssertionError(f"Wrong {k} {ident}: {meta.get(k)!r}")
 if meta["mesh_objects"]<2 or meta["polygons"]<100:
  raise AssertionError("Suspicious primitive-only model: "+ident)
 if meta["materials"]<1:raise AssertionError("No materials: "+ident)
 with Image.open(folder/"preview.png") as im:
  im.load()
  if im.size!=EXPECTED:raise AssertionError("Incorrect image size "+ident)
  gray=im.convert("L")
  contrast=float(ImageStat.Stat(gray).stddev[0])
  bg=im.convert("RGB").getpixel((5,5))
  from PIL import Image as Img
  background=Img.new("RGB",im.size,bg)
  diff=ImageChops.difference(im.convert("RGB"),background).convert("L")
  visible=diff.point(lambda n:255 if n>14 else 0).getbbox()
  if visible is None:raise AssertionError("Blank asset "+ident)
  coverage=diff.point(lambda n:255 if n>14 else 0).histogram()[255]
  try:bbox_width,bbox_height=validate_silhouette(visible,coverage)
  except AssertionError as err:raise AssertionError(f"{ident}: {err}") from err
  if contrast<7:raise AssertionError(f"Very low contrast {ident}: {contrast:.2f}")
 probe=subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0",
  "-show_entries","stream=nb_frames,width,height","-of","json",
  str(folder/"turntable.mp4")],text=True)
 track=json.loads(probe)["streams"][0]
 if int(track["nb_frames"])!=144 or (track["width"],track["height"])!=EXPECTED:
  raise AssertionError("Invalid turntable video: "+ident)
 return {"id":ident,"title":title,"category":category,
  "mesh_objects":meta["mesh_objects"],"polygons":meta["polygons"],
  "preview_stddev":round(contrast,2),"preview_frame":meta["preview_frame"],
  "image_bbox":[bbox_width,bbox_height],"visible_pixels":coverage,
  "bytes":sum((folder/name).stat().st_size for name in files)}
def main():
 args=sys.argv[1:]
 if "--all" in args:rows=CATALOG;whole=True
 else:
  if "--batch" not in args:raise ValueError("--batch N or --all")
  batch=int(args[args.index("--batch")+1])
  if batch not in range(10):raise ValueError("Out-of-range batch")
  rows=CATALOG[batch*10:(batch+1)*10];whole=False
 results=[check(row) for row in rows]
 if len(results)!=(100 if whole else 10):raise AssertionError("Wrong subject count")
 record={"validated":len(results),"total_polygons":sum(x["polygons"] for x in results),
         "total_parts":sum(x["mesh_objects"] for x in results),
         "lowest_contrast":min(x["preview_stddev"] for x in results),
         "items":results}
 filename=OUT/("validation-all.json" if whole else "validation-batch.json")
 filename.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("REBUILT_VERIFIED",len(results),"faces",record["total_polygons"],
       "parts",record["total_parts"],"mincontrast",record["lowest_contrast"])
if __name__=="__main__":main()
