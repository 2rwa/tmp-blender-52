"""Claude Sonnet 5.5 Medium: five Workbench color-test subjects."""
CATALOG=[
 ("craft_wagasa","和傘","craft",0),
 ("craft_chochin","提灯","craft",1),
 ("craft_sensu","扇子","craft",2),
 ("gakki_tsuzumi","鼓","gakki",3),
 ("ritual_suzu","神楽鈴","ritual",4)
]
assert len(CATALOG)==5 and len({x[0] for x in CATALOG})==5
