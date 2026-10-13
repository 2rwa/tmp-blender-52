"""100 distinct Japanese traditional crafts and household objects."""
GROUPS = {
    "tea": [("chawan", "茶碗"), ("chasen", "茶筅"), ("chashaku", "茶杓"), ("natsume", "棗"), ("tetsubin", "鉄瓶"), ("kyusu", "急須"), ("chagama", "茶釜"), ("mizusashi", "水指"), ("hishaku", "柄杓"), ("futaoki", "蓋置")],
    "kitchen": [("yunomi", "湯呑"), ("tokkuri", "徳利"), ("ochoko", "お猪口"), ("suribachi", "すり鉢"), ("surikogi", "すりこぎ"), ("hangiri", "飯切"), ("ohitsu", "お櫃"), ("seiro", "せいろ"), ("jubako", "重箱"), ("shamoji", "しゃもじ")],
    "bamboo": [("zaru", "笊"), ("takekago", "竹籠"), ("hanaire", "竹花入"), ("takezaiku_box", "竹細工箱"), ("sudare", "簾"), ("chasho", "茶筒"), ("takeshibuki", "竹水差し"), ("takebue", "篠笛"), ("take_tombo", "竹とんぼ"), ("houki", "箒")],
    "home": [("andon", "行灯"), ("chochin", "提灯"), ("bonbori", "雪洞"), ("hibachi", "火鉢"), ("kaya", "蚊帳"), ("noren", "暖簾"), ("byobu", "屏風"), ("tatami", "畳"), ("zabuton", "座布団"), ("furin", "風鈴")],
    "wear": [("sensu", "扇子"), ("uchiwa", "団扇"), ("wagasa", "和傘"), ("geta", "下駄"), ("zori", "草履"), ("tabi", "足袋"), ("kanzashi", "簪"), ("kinchaku", "巾着"), ("furoshiki", "風呂敷"), ("tenugui", "手拭")],
    "writing": [("suzuri", "硯"), ("fude", "筆"), ("sumi", "墨"), ("bunchin", "文鎮"), ("makimono", "巻物"), ("washi", "和紙"), ("suzuribako", "硯箱"), ("hanko", "判子"), ("inro", "印籠"), ("kakejiku", "掛軸")],
    "folk": [("daruma", "だるま"), ("kokeshi", "こけし"), ("manekineko", "招き猫"), ("kendama", "けん玉"), ("koma", "独楽"), ("hagoita", "羽子板"), ("otedama", "お手玉"), ("denden_daiko", "でんでん太鼓"), ("akabeko", "赤べこ"), ("hariko_tora", "張子の虎")],
    "ritual": [("ema", "絵馬"), ("omamori", "お守り"), ("shimenawa", "注連縄"), ("suzu", "神楽鈴"), ("omikuji", "おみくじ"), ("gohei", "御幣"), ("hamaya", "破魔矢"), ("shide", "紙垂"), ("masu", "枡"), ("kagami_mochi", "鏡餅飾り")],
    "woodwork": [("tansu", "和箪笥"), ("chabudai", "ちゃぶ台"), ("zaisu", "座椅子"), ("kotatsu", "炬燵"), ("nagamochi", "長持"), ("tsuitate", "衝立"), ("shodana", "書棚"), ("fumikiri", "踏み台"), ("obon", "木盆"), ("kumiko", "組子細工")],
    "craft": [("koro", "香炉"), ("orin", "おりん"), ("mokugyo", "木魚"), ("kiriko", "切子グラス"), ("shikki_wan", "漆器椀"), ("makie_bako", "蒔絵箱"), ("kabuto_ornament", "兜飾り"), ("kazaridaru", "飾り樽"), ("sake_flask", "錫製酒器"), ("kumihimo", "組紐")],
}
CATALOG = [(f"{group}_{slug}", jp, group, i) for group, items in GROUPS.items() for i, (slug, jp) in enumerate(items)]
assert len(CATALOG) == 100 and len({p[0] for p in CATALOG}) == 100
