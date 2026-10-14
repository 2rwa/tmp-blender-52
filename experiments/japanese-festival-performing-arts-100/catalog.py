"""Japanese festival and performance arts: 100 individually modeled objects."""
GROUPS = {
    "matsuri": [("mikoshi", "神輿"), ("mikoshi_phoenix", "鳳凰付き神輿"), ("danjiri", "だんじり"), ("hikiyama", "曳山"), ("yatai_float", "屋台山車"), ("hoko_float", "鉾"), ("taikodai", "太鼓台"), ("kasaboko", "笠鉾"), ("lantern_tower", "祭礼提灯台"), ("float_wheel", "山車車輪")],
    "ritual": [("chochin", "提灯"), ("takachochin_pole", "高張提灯"), ("shimenawa_gate", "注連縄飾り"), ("shide_bundle", "紙垂束"), ("sakaki_branch", "榊"), ("ema_stand", "絵馬掛け"), ("omamori_rack", "御守掛け"), ("saisen_box", "賽銭箱"), ("temizuya_ladle", "手水舎の柄杓"), ("festival_lantern", "祭礼灯籠")],
    "shinji": [("gohei", "御幣"), ("kagura_suzu", "神楽鈴"), ("haraegushi", "祓串"), ("eboshi", "烏帽子"), ("shaku", "笏"), ("houbei_tray", "奉幣盆"), ("sanbo", "三方"), ("ritual_drum", "神事太鼓"), ("ritual_fan", "神事扇"), ("sakaki_stand", "榊立て")],
    "gakki": [("nagadou_taiko", "長胴太鼓"), ("shime_daiko", "締太鼓"), ("okedo_daiko", "桶胴太鼓"), ("uchiwa_daiko", "団扇太鼓"), ("atarigane", "当り鉦"), ("kane_bachi", "鉦と撞木"), ("shinobue", "篠笛"), ("ryuteki", "龍笛"), ("horagai", "法螺貝"), ("sasara", "簓")],
    "noh": [("koomote_mask", "小面"), ("hannya_mask", "般若面"), ("okina_mask", "翁面"), ("tengu_mask", "天狗面"), ("folding_fan", "能扇"), ("kotsuzumi", "小鼓"), ("otsuzumi", "大鼓"), ("nokan", "能管"), ("costume_karaori", "唐織"), ("stage_pine_panel", "鏡板")],
    "kabuki": [("kumadori_mask", "隈取面"), ("mie_fan", "見得扇"), ("hikinuki_costume", "引抜衣装"), ("kasa_hat", "歌舞伎笠"), ("hyoshigi", "拍子木"), ("tsukeita", "附け板"), ("kurogo_hood", "黒衣頭巾"), ("stage_lantern", "芝居提灯"), ("onnagata_kanzashi", "女形簪"), ("kiseru_prop", "煙管小道具")],
    "buyo_folk": [("sensu", "舞扇"), ("suzu", "舞鈴"), ("kasa", "舞傘"), ("tenugui", "手拭"), ("mai_ogi", "舞用扇"), ("shishimai_head", "獅子頭"), ("shishimai_cloth", "獅子舞胴幕"), ("kitsune_mask", "狐面"), ("oni_mask", "鬼面"), ("binzasara", "びんざさら")],
    "costume": [("happi", "法被"), ("hachimaki", "鉢巻"), ("tabi", "足袋"), ("waraji", "草鞋"), ("geta_festival", "祭下駄"), ("bell_anklet", "鈴脚絆"), ("miko_chihaya", "千早"), ("miko_hakama", "緋袴"), ("yamabushi_tokin", "頭襟"), ("horagai_strap", "法螺貝紐")],
    "stage": [("torii_prop", "鳥居小道具"), ("kagamiita_panel", "鏡板パネル"), ("byobu_gold", "金屏風"), ("bonbori", "雪洞"), ("andon", "行灯"), ("noren_festival", "祭暖簾"), ("yagura_tower", "櫓"), ("lantern_string", "提灯列"), ("kouhaku_curtain", "紅白幕"), ("drum_stand", "太鼓台")],
    "local": [("namahage_mask", "なまはげ面"), ("namahage_knife_prop", "なまはげ包丁小道具"), ("dekonnbo_mask", "デコンボ面"), ("hyakumangoku_helmet", "郷土祭礼兜"), ("awaodori_fan", "阿波踊り団扇"), ("awaodori_amigasa", "阿波踊り編笠"), ("eisa_paranku", "エイサー・パーランクー"), ("eisa_odaiko", "エイサー大太鼓"), ("kasaodori_hat", "笠踊り笠"), ("dengaku_hoe_prop", "田楽鍬小道具")],
}
CATALOG = [(f"{group}_{slug}", title, group, variant) for group, items in GROUPS.items() for variant, (slug, title) in enumerate(items)]
assert len(CATALOG)==100 and len({row[0] for row in CATALOG})==100
