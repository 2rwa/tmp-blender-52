"""Verify actual deliverables (not merely Blender exit codes)."""
import json
import subprocess
import sys
from pathlib import Path
from PIL import Image,ImageStat
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from catalog import CATALOG
ROOT=Path("output52")
def validate_row(row):
 ident,title,category,_=row
 folder=ROOT/"items"/ident
 sizes={"preview.png":2000,"turntable.mp4":3000,
        ident+".blend":1500,ident+".glb":700,"metadata.json":200}
 for filename,min_bytes in sizes.items():
  path=folder/filename
  if not path.is_file() or path.stat().st_size<min_bytes:
   raise AssertionError(f"Missing/small {path}")
 assert (folder/(ident+".blend")).open("rb").read(7)==b"BLENDER",ident
 assert (folder/(ident+".glb")).open("rb").read(4)==b"glTF",ident
 assert (folder/"preview.png").open("rb").read(8)==b"\x89PNG\r\n\x1a\n",ident
 meta=json.loads((folder/"metadata.json").read_text(encoding="utf-8"))
 assert meta["id"]==ident and meta["title"]==title and meta["category"]==category,ident
 assert meta["mesh_objects"]>0 and meta["polygons"]>=10,ident
 assert meta["frames"]==144 and meta["fps"]==24 and meta["resolution"]==[400,300],ident
 assert str(meta["blender_version"]).startswith("5.2."),ident
 with Image.open(folder/"preview.png") as image:
  image.load()
  assert image.size==(400,300),ident
  dev=ImageStat.Stat(image.convert("L")).stddev[0]
  assert dev>8, f"Nearly blank frame {ident} stddev={dev}"
 probe=subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0",
   "-show_entries","stream=nb_frames,width,height","-of","json",
   str(folder/"turntable.mp4")],text=True)
 stream=json.loads(probe)["streams"][0]
 assert int(stream["nb_frames"])==144 and (stream["width"],stream["height"])==(400,300),ident
 return {"id":ident,"title":title,"category":category,"polygons":meta["polygons"],
         "preview_stddev":round(dev,2),"size_bytes":sum((folder/k).stat().st_size for k in sizes)}
def main():
 args=sys.argv[1:]
 all_assets="--all" in args
 if all_assets:rows=CATALOG
 else:
  assert "--batch" in args,"Use --batch N or --all"
  batch=int(args[args.index("--batch")+1])
  assert 0<=batch<10
  rows=CATALOG[batch*10:batch*10+10]
 result=[validate_row(row) for row in rows]
 assert len(result)==(100 if all_assets else 10)
 report={"validated":len(result),"total_polygons":sum(x["polygons"] for x in result),
         "items":result}
 path=ROOT/("validation-all.json" if all_assets else "validation-batch.json")
 path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(f"VALIDATED {len(result)} models, polygons={report['total_polygons']}")
if __name__=="__main__":main()
