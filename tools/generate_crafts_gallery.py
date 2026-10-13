"""Generate a 100-item gallery using validated GitHub-stored Blender results."""
import html
import json
import os
import shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"results"/"japanese-crafts-100"
DOCS=ROOT/"docs"
DEST=DOCS/"crafts"
def main():
 catalog=BASE/"catalog.json"
 if not catalog.exists():
  print("Craft assets not yet rendered; skipping gallery.")
  return
 raw=json.loads(catalog.read_text(encoding="utf-8"))
 items=raw["items"]
 assert len(items)==100 and len({x["id"] for x in items})==100
 repo=os.environ.get("GITHUB_REPOSITORY","2rwa/tmp-blender-52")
 assert len(repo.split("/"))==2
 DEST.mkdir(parents=True,exist_ok=True)
 (DEST/"previews").mkdir(exist_ok=True)
 groups={}
 cards=[]
 for item in items:
  ident=item["id"];name=item["title"];category=item["category"]
  assert ident.replace("_","").isalnum()
  source=BASE/"items"/ident
  thumb=source/"preview.png"
  assert thumb.is_file(),thumb
  shutil.copy2(thumb,DEST/"previews"/(ident+".png"))
  root=f"https://raw.githubusercontent.com/{repo}/main/results/japanese-crafts-100/items/{ident}/{ident}"
  mp4=f"https://raw.githubusercontent.com/{repo}/main/results/japanese-crafts-100/items/{ident}/turntable.mp4"
  groups[category]=groups.get(category,0)+1
  cards.append(f"""<article class="card" data-category="{category}" data-search="{ident} {html.escape(name)}">
   <img loading="lazy" width="400" height="300" src="previews/{ident}.png" alt="{html.escape(name)}">
   <div class="info"><b>{html.escape(name)}</b><small>{ident} · {item['polygons']} faces</small>
   <div class="links"><a download href="{root}.blend">.blend</a>
   <a download href="{root}.glb">.glb</a><button data-video="{mp4}">▶ 回転</button></div></div></article>""")
 options=''.join(f'<option value="{k}">{k} ({v})</option>' for k,v in groups.items())
 page="""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>日本の伝統工芸・生活道具 100 | Blender low-poly</title>
<style>
:root{font-family:system-ui,sans-serif;color-scheme:dark}
*{box-sizing:border-box}body{margin:0;background:#10151b;color:#f0eee6}
header{padding:22px;position:sticky;top:0;background:#10151bf0;z-index:2;border-bottom:1px solid #353b44}
h1{font-size:clamp(1.2rem,3vw,2rem);margin:0 0 5px}p{color:#adb7c2;margin:8px 0}
nav{display:flex;gap:12px;flex-wrap:wrap;margin-top:12px}
input,select{background:#242e38;color:#fff;border:1px solid #58616a;border-radius:8px;padding:11px;min-width:175px}
input{flex:1}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(245px,1fr));gap:16px;padding:18px;max-width:1500px;margin:auto}
.card{background:#1c252f;border:1px solid #394351;border-radius:12px;overflow:hidden}
.card img,.card video{width:100%;aspect-ratio:4/3;object-fit:cover;display:block;background:#27323f}
.info{padding:14px;display:grid;gap:6px}.info small{color:#aab9c9;overflow-wrap:anywhere}
.links{display:flex;gap:7px;flex-wrap:wrap;margin-top:6px}.links a,.links button{background:#3b5164;border:1px solid #637991;border-radius:7px;color:#fff;padding:7px 10px;font:inherit;text-decoration:none;cursor:pointer}
.back{color:#d3e3fc}#count{font-weight:bold}
</style></head><body><header><a class="back" href="../">← 全実験ギャラリーへ</a>
<h1>日本の伝統工芸・生活道具 — 100種</h1>
<p>Blender 5.2 / スタイライズ・ローポリ / 6秒・24fps Workbenchターンテーブル</p>
<nav><input type="search" id="filter" placeholder="作品名・IDで検索"><select id="category"><option value="">全カテゴリー (100)</option>"""+options+"""</select><span id="count">100件</span></nav>
</header><main class="grid" id="grid">"""+'\n'.join(cards)+"""</main>
<script>
const q=document.querySelector('#filter'),cat=document.querySelector('#category');
function update(){let n=0;document.querySelectorAll('.card').forEach(el=>{
const ok=(!cat.value||el.dataset.category===cat.value)&&el.dataset.search.toLowerCase().includes(q.value.trim().toLowerCase());
el.hidden=!ok;if(ok)n++;});document.querySelector('#count').textContent=n+'件';}
q.addEventListener('input',update);cat.addEventListener('change',update);
document.addEventListener('click',e=>{const button=e.target.closest('button[data-video]');if(!button)return;
const card=button.closest('.card'),img=card.querySelector('img');if(img){const v=document.createElement('video');
v.src=button.dataset.video;v.controls=true;v.autoplay=true;v.loop=true;v.playsInline=true;img.replaceWith(v);}
button.disabled=true;});
</script></body></html>"""
 (DEST/"index.html").write_text(page,encoding="utf-8")
 index=DOCS/"index.html"
 mainpage=index.read_text(encoding="utf-8")
 entry='<p><a href="crafts/" style="color:#ffd58a;font-weight:bold">日本の伝統工芸・生活道具 100種を見る →</a></p>'
 if entry not in mainpage:
  index.write_text(mainpage.replace("</header>",entry+"</header>",1),encoding="utf-8")
 print("Generated Japanese craft Pages gallery:",len(items))
if __name__=="__main__":main()
