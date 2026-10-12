"""Validate actual Workbench renders and editable model outputs."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

ID = 'chesterfield-workbench'
OUT = Path('output52')
FRAMES = OUT / 'frames'


def check_file(path, minimum):
    if not path.is_file() or path.stat().st_size < minimum:
        raise SystemExit('Missing/undersized: '+str(path))


def main():
    report_path=OUT/(ID+'-report.json')
    preview=OUT/'preview.png'
    movie=OUT/(ID+'.mp4')
    blend=OUT/(ID+'.blend')
    version=OUT/'blender-version.txt'
    for path,size in ((report_path,500),(preview,5000),(movie,10000),
                      (blend,50000),(version,100)):
        check_file(path,size)
    if 'Blender 5.2.2' not in version.read_text(errors='replace'):
        raise SystemExit('Incorrect Blender version')
    r=json.loads(report_path.read_text(encoding='utf-8'))
    if not str(r.get('blender_version','')).startswith('5.2.2'):
        raise SystemExit('Report version mismatch')
    if r.get('engine')!='BLENDER_WORKBENCH':
        raise SystemExit('Expected Workbench renderer')
    if r.get('resolution')!=[1280,720] or r.get('frame_count')!=96:
        raise SystemExit('HD resolution/frame count mismatch')
    c=r['component_counts']
    for name,value in (('tufted_panels',4),('wings',2),('arm_scrolls',2),
                       ('bun_feet',4),('nailheads',81)):
        if c.get(name)!=value:
            raise SystemExit('%s expected %s, received %s'%(name,value,c.get(name)))
    if c['buttons']<55 or c['diamond_seams']<45 or r['mesh_object_count']<130:
        raise SystemExit('Detailed model topology incomplete')
    frames=sorted(FRAMES.glob('frame_*.png'))
    if len(frames)!=96:
        raise SystemExit('Expected 96 PNGs, found %s'%len(frames))
    with Image.open(preview) as im:
        if im.size!=(1280,720):
            raise SystemExit('Preview dimensions incorrect')
        gray=im.convert('L')
        contrast=gray.getextrema()[1]-gray.getextrema()[0]
        std=float(ImageStat.Stat(gray).stddev[0])
    if contrast<45 or std<12:
        raise SystemExit('Preview looks empty/flat: contrast %s std %.2f'%(contrast,std))
    with Image.open(frames[0]) as a,Image.open(frames[23]) as b:
        diff=ImageChops.difference(a.convert('RGB'),b.convert('RGB'))
        motion=sum(ImageStat.Stat(diff).mean)/3
    if motion<1.5:
        raise SystemExit('Camera did not visibly orbit: %.3f'%motion)
    output={
        'experiment':ID,'status':'validated',
        'blender_version':r['blender_version'], 'engine':r['engine'],
        'resolution':r['resolution'],'frame_count':len(frames),
        'component_counts':c,'mesh_object_count':r['mesh_object_count'],
        'preview_contrast':contrast,'preview_stddev':round(std,3),
        'frame_1_to_24_difference':round(motion,3),
        'blend_size_bytes':blend.stat().st_size,
        'video_size_bytes':movie.stat().st_size,
        'preview_sha256':hashlib.sha256(preview.read_bytes()).hexdigest(),
    }
    (OUT/'validation.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))


if __name__ == '__main__':
    main()
