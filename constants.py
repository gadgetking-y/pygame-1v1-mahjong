import os
SCREEN_W, SCREEN_H, FPS = 1200, 850, 60
COLOR_TABLE = (34, 139, 34)
COLOR_WHITE, COLOR_BLACK, COLOR_GOLD = (255,255,255), (0,0,0), (255,215,0)
COLOR_TILE_BACK, COLOR_TILE_BODY, COLOR_SHADOW = (255,120,0), (255,255,250), (20,60,20)
TILE_W, TILE_H = 54, 72
HAND_Y, HAND_X, SPACING, GAP = 740, 200, 56, 25
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
HONOR_NAMES = {1: "東", 2: "南", 3: "西", 4: "北", 5: "白", 6: "發", 7: "中"}
IMAGE_FN = {"Front": "Front.png", "Back": "Back.png", "M1": "Man1.png", "M9": "Man9.png", "P1": "Pin1.png", "P2": "Pin2.png", "P3": "Pin3.png", "P4": "Pin4.png", "P5": "Pin5.png", "P6": "Pin6.png", "P7": "Pin7.png", "P8": "Pin8.png", "P9": "Pin9.png", "S1": "Sou1.png", "S2": "Sou2.png", "S3": "Sou3.png", "S4": "Sou4.png", "S5": "Sou5.png", "S6": "Sou6.png", "S7": "Sou7.png", "S8": "Sou8.png", "S9": "Sou9.png", "H1": "Ton.png", "H2": "Nan.png", "H3": "Shaa.png", "H4": "Pei.png", "H5": "Haku.png", "H6": "Hatsu.png", "H7": "Chun.png"}

YAKU_JA = {
    "Riichi": "立直", "Tanyao": "断么九", "Menzen Tsumo": "門前清自摸和",
    "Pinfu": "平和", "Iipeiko": "一盃口", "Yakuhai (haku)": "役牌(白)",
    "Yakuhai (hatsu)": "役牌(發)", "Yakuhai (chun)": "役牌(中)",
    "Toitoi": "対々和", "Sananko": "三暗刻", "Chiitoitsu": "七対子",
    "Honitsu": "混一色", "Chinitsu": "清一色", "Ittsu": "一気通貫",
    "Sanshoku": "三色同順", "Chanta": "混全帯么九", "Honroutou": "混老頭",
    "Dora": "ドラ", "Ura Dora": "裏ドラ", "Aka Dora": "赤ドラ", "Ippatsu": "一発"
}
