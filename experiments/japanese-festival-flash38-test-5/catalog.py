"""Five isolated Gemini 3.8 Flash Low model-generation test items."""
CATALOG=[
 ("matsuri_mikoshi","神輿","matsuri",0),
 ("gakki_ryuteki","龍笛","gakki",1),
 ("kabuki_kiseru_prop","煙管","kabuki",2),
 ("local_dengaku_hoe_prop","田楽の鍬小道具","local",3),
 ("stage_yagura_tower","祭礼の櫓","stage",4)
]
assert len(CATALOG)==5 and len({x[0] for x in CATALOG})==5
