import pygame, os, urllib.request
from constants import IMAGE_FN, HONOR_NAMES, YAKU_JA

def download_assets(assets_dir):
    if not os.path.exists(assets_dir): os.makedirs(assets_dir)
    for f in IMAGE_FN.values():
        p = os.path.join(assets_dir, f)
        if not os.path.exists(p):
            try: urllib.request.urlretrieve("https://raw.githubusercontent.com/FluffyStuff/riichi-mahjong-tiles/master/Export/Regular/" + f, p)
            except: pass

class UIDrawer:
    def __init__(self, screen, assets_dir, w, h):
        self.screen = screen; self.imgs = {}; self.tile_w, self.tile_h = w, h
        for k, f in IMAGE_FN.items():
            p = os.path.join(assets_dir, f)
            if os.path.exists(p):
                base_img = pygame.image.load(p).convert_alpha()
                self.imgs[k] = pygame.transform.smoothscale(base_img, (w, h))
                # 横向き用の画像も生成
                self.imgs[k + "_H"] = pygame.transform.rotate(self.imgs[k], 90)
        
        ja_f = ["hiraginosansgbw3", "msgothic", "stheitimedium", "arialunicode", "applesdgothicneo", "notosanscjkjp"]
        fn = next((f for f in ja_f if f in pygame.font.get_fonts()), None)
        self.ui_f = pygame.font.SysFont(fn, 24)
        self.tl_f = pygame.font.SysFont(fn, 32, bold=True)
        self.bg_f = pygame.font.SysFont(fn, 64, bold=True)

    def draw_t(self, x, y, name, back=False, highlight=False, horizontal=False, compact_horizontal=False):
        # 横向きの場合は画像とサイズを切り替え
        suffix = "_H" if horizontal else ""
        if horizontal and compact_horizontal:
            w, h = self.tile_w, max(1, int(self.tile_w * self.tile_w / self.tile_h))
            y = y + (self.tile_h - h) // 2
        else:
            w, h = (self.tile_h, self.tile_w) if horizontal else (self.tile_w, self.tile_h)
        rect = pygame.Rect(x, y, w, h)
        
        pygame.draw.rect(self.screen, (20,60,20), rect.move(3,3), border_radius=4)
        pygame.draw.rect(self.screen, (255,255,250) if not back else (255,120,0), rect, border_radius=4)
        
        img_key = "Back" + suffix if back else (name + suffix if name else "Front" + suffix)
        img = self.imgs.get(img_key)
        
        if img:
            if horizontal and compact_horizontal:
                img = pygame.transform.smoothscale(img, (w, h))
            self.screen.blit(img, (x, y))
        elif not back and name:
            s = self.tl_f.render(name, True, (0,0,0))
            if horizontal: s = pygame.transform.rotate(s, 90)
            self.screen.blit(s, s.get_rect(center=rect.center))
            
        pygame.draw.rect(self.screen, (0,0,0), rect, 1, border_radius=4)
        if highlight: pygame.draw.rect(self.screen, (255,215,0), rect, 3, border_radius=4)

    def draw_riichi_stick(self, x, y):
        """リーチ点棒を描画"""
        stick_rect = pygame.Rect(x, y, 100, 15)
        pygame.draw.rect(self.screen, (240, 240, 240), stick_rect, border_radius=5)
        pygame.draw.rect(self.screen, (0, 0, 0), stick_rect, 1, border_radius=5)
        pygame.draw.circle(self.screen, (200, 0, 0), (x + 50, y + 7), 4) # 中央の赤い点

    def draw_msg(self, msg, yaku_res, han, fu, cost):
        panel = pygame.Rect((self.screen.get_width() - 700) // 2, 100, 700, 650)
        pygame.draw.rect(self.screen, (0,0,0,230), panel, border_radius=15)
        pygame.draw.rect(self.screen, (255,215,0), panel, 2, border_radius=15)
        txt = self.bg_f.render(msg, True, (255,215,0))
        self.screen.blit(txt, txt.get_rect(center=(panel.centerx, 180)))
        info_s = self.tl_f.render(f"{han}翻 {fu}符  合計 {cost}点", True, (255,255,255))
        self.screen.blit(info_s, info_s.get_rect(center=(panel.centerx, 250)))
        for i, y in enumerate(yaku_res[:12]):
            ja_n = YAKU_JA.get(y['name'], y['name'])
            name_s = self.ui_f.render(ja_n, True, (220,220,220))
            han_s = self.ui_f.render(f"{y['han']}翻", True, (255,255,250))
            self.screen.blit(name_s, (panel.x + 150, 300 + i*32)); self.screen.blit(han_s, (panel.right - 200, 300 + i*32))
        self.screen.blit(self.ui_f.render("Spaceキーで次局へ", True, (255,215,0)), (panel.centerx - 100, 700))
