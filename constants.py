import os
SCREEN_W, SCREEN_H, FPS = 1500, 850, 60
COLOR_TABLE = (20, 96, 52)
COLOR_TABLE_BORDER = (15, 70, 38)
COLOR_WHITE, COLOR_BLACK, COLOR_GOLD = (255,255,255), (20,20,20), (255,215,0)
COLOR_CYAN = (0, 220, 255)
COLOR_TILE_BACK, COLOR_TILE_BODY, COLOR_SHADOW = (240,110,20), (255,255,250), (10,35,15)
TILE_W, TILE_H = 48, 64
HAND_Y, HAND_X, SPACING, GAP = 745, 220, 50, 18
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
HONOR_NAMES = {1: "東", 2: "南", 3: "西", 4: "北", 5: "白", 6: "發", 7: "中"}
IMAGE_FN = {"Front": "Front.png", "Back": "Back.png", "M1": "Man1.png", "M2": "Man2.png", "M3": "Man3.png", "M4": "Man4.png", "M5": "Man5.png", "M6": "Man6.png", "M7": "Man7.png", "M8": "Man8.png", "M9": "Man9.png", "P1": "Pin1.png", "P2": "Pin2.png", "P3": "Pin3.png", "P4": "Pin4.png", "P5": "Pin5.png", "P6": "Pin6.png", "P7": "Pin7.png", "P8": "Pin8.png", "P9": "Pin9.png", "S1": "Sou1.png", "S2": "Sou2.png", "S3": "Sou3.png", "S4": "Sou4.png", "S5": "Sou5.png", "S6": "Sou6.png", "S7": "Sou7.png", "S8": "Sou8.png", "S9": "Sou9.png", "H1": "Ton.png", "H2": "Nan.png", "H3": "Shaa.png", "H4": "Pei.png", "H5": "Haku.png", "H6": "Hatsu.png", "H7": "Chun.png"}


YAKU_JA = {
    "Riichi": "立直", "Tanyao": "断么九", "Menzen Tsumo": "門前清自摸和", "Pinfu": "平和", "Iipeiko": "一盃口", "Yakuhai (haku)": "役牌(白)", "Yakuhai (hatsu)": "役牌(發)", "Yakuhai (chun)": "役牌(中)", "Yakuhai (east)": "役牌(東)", "Yakuhai (south)": "役牌(南)", "Yakuhai (round wind east)": "場風牌(東)", "Yakuhai (round wind south)": "場風牌(南)", "Yakuhai (seat wind east)": "自風牌(東)", "Yakuhai (seat wind south)": "自風牌(南)", "Toitoi": "対々和", "Sananko": "三暗刻", "Chiitoitsu": "七対子", "Honitsu": "混一色", "Chinitsu": "清一色", "Ittsu": "一気通貫", "Sanshoku": "三色同順", "Chanta": "混全帯么九", "Honroutou": "混老頭", "Dora": "ドラ", "Ura Dora": "裏ドラ", "Aka Dora": "赤ドラ", "Ippatsu": "一発", "Rinshan Kaihou": "嶺上開花", "Haitei Raoyue": "海底摸月", "Houtei Raoyui": "河底撈魚"
}

