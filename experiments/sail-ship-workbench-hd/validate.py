"""Assert Workbench settings, modeled components, PNGs and observable motion."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from PIL import Image,ImageChops,ImageStat

ID="sail-ship-workbench-hd"
OUT=Path("output52")
FRAMES=OUT/"frames"

def file(path,minimum):
    if not path.is_file() or path.stat().st_size<minimum:
        raise SystemExit("Missing or undersized artifact: %s"%path)

def main():
    report_path=OUT/(ID+"-report.json")
    preview=OUT/"preview.png"
    blend=OUT/(ID+".blend")
    video=OUT/(ID+".mp4")
    version=OUT/"blender-version.txt"
    for path,size in [(report_path,1000),(preview,10000),
                      (blend,50000),(video,15000),(version,100)]:
        file(path,size)
    if "Blender 5.2.2" not in version.read_text(errors="replace"):
        raise SystemExit("Unexpected Blender version")
    r=json.loads(report_path.read_text())
    if not r["blender_version"].startswith("5.2.2"):
        raise SystemExit("Not Blender 5.2.2")
    if r["engine"]!="BLENDER_WORKBENCH":
        raise SystemExit("Not Workbench: "+r["engine"])
    if r["resolution"]!=[1280,720] or r["frame_count"]!=120:
        raise SystemExit("Incorrect HD resolution or duration")
    counts=r["component_counts"]
    for key,expected in [("masts",3),("sails",6),("yards",5),
                         ("portholes",22)]:
        if counts[key]!=expected:
            raise SystemExit("Unexpected %s: %s"%(key,counts[key]))
    if r["mesh_object_count"]<75:
        raise SystemExit("Incomplete mesh count")
    images=sorted(FRAMES.glob("frame_*.png"))
    if len(images)!=120:
        raise SystemExit("Missing image frames: %d"%len(images))
    with Image.open(preview) as p:
        p.load()
        if p.size!=(1280,720):
            raise SystemExit("Wrong preview size")
        gray=p.convert("L")
        lo,hi=gray.getextrema()
        std=float(ImageStat.Stat(gray).stddev[0])
    if hi-lo<42 or std<10:
        raise SystemExit("Preview too flat: contrast %d std %.2f"%(hi-lo,std))
    with Image.open(images[0]) as x,Image.open(images[30]) as y:
        diff=ImageChops.difference(x.convert("RGB"),y.convert("RGB"))
        movement=sum(ImageStat.Stat(diff).mean)/3
    if movement<1.8:
        raise SystemExit("No visible turntable motion: %.3f"%movement)
    result={"experiment":ID,"status":"validated",
            "engine":r["engine"],"blender_version":r["blender_version"],
            "resolution":r["resolution"],"frame_count":len(images),
            "mesh_object_count":r["mesh_object_count"],
            "component_counts":counts,"preview_stddev":round(std,3),
            "motion_difference":round(movement,3),
            "blend_size_bytes":blend.stat().st_size,
            "video_size_bytes":video.stat().st_size,
            "preview_sha256":hashlib.sha256(preview.read_bytes()).hexdigest()}
    (OUT/"validation.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
