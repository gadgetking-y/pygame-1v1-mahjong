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
                self.imgs[k + "_H"] = pygame.transform.rotate(self.imgs[k], 90)
        
        ja_f = ["hiraginosansgbw3", "msgothic", "stheitimedium", "arialunicode", "applesdgothicneo", "notosanscjkjp"]
        fn = next((f for f in ja_f if f in pygame.font.get_fonts()), None)
        self.sm_f = pygame.font.SysFont(fn, 16, bold=True)
        self.ui_f = pygame.font.SysFont(fn, 22)
        self.tl_f = pygame.font.SysFont(fn, 28, bold=True)
        self.bg_f = pygame.font.SysFont(fn, 56, bold=True)


    def draw_t(self, x, y, name, back=False, highlight=False, horizontal=False, scale=1.0):
        """牌を描画。横向き（リーチ）の場合は縦横比を正しく保って幅tile_h * scale, 高さtile_w * scaleで描画"""
        bw = int((self.tile_h if horizontal else self.tile_w) * scale)
        bh = int((self.tile_w if horizontal else self.tile_h) * scale)
        rect = pygame.Rect(x, y, bw, bh)
        
        # 影と本体
        pygame.draw.rect(self.screen, (10, 35, 15), rect.move(2, 3), border_radius=4)
        body_color = (240, 110, 20) if back else (255, 255, 250)
        pygame.draw.rect(self.screen, body_color, rect, border_radius=4)
        
        suffix = "_H" if horizontal else ""
        img_key = "Back" + suffix if back else (name + suffix if name else "Front" + suffix)
        img = self.imgs.get(img_key)
        
        if img:
            if scale != 1.0:
                img = pygame.transform.smoothscale(img, (bw, bh))
            self.screen.blit(img, (x, y))
        elif not back and name:
            s = self.ui_f.render(name, True, (0,0,0))
            if horizontal: s = pygame.transform.rotate(s, 90)
            self.screen.blit(s, s.get_rect(center=rect.center))
            
        border_col = (255, 215, 0) if highlight else (40, 40, 40)
        border_w = 2 if highlight else 1
        pygame.draw.rect(self.screen, border_col, rect, border_w, border_radius=4)

    def draw_riichi_stick(self, x, y):
        """立体感のあるきれいな1000点リーチ棒を描画"""
        stick_rect = pygame.Rect(x, y, 110, 14)
        shadow_rect = stick_rect.move(2, 2)
        pygame.draw.rect(self.screen, (10, 30, 15, 120), shadow_rect, border_radius=7)
        pygame.draw.rect(self.screen, (245, 245, 242), stick_rect, border_radius=7)
        pygame.draw.rect(self.screen, (180, 180, 175), stick_rect, 1, border_radius=7)
        # 中央の点
        pygame.draw.circle(self.screen, (220, 20, 20), (x + 55, y + 7), 4)
        pygame.draw.circle(self.screen, (255, 100, 100), (x + 54, y + 6), 1)

    def draw_msg(self, msg, yaku_res, han, fu, cost):
        panel = pygame.Rect((self.screen.get_width() - 680) // 2, 110, 680, 630)
        pygame.draw.rect(self.screen, (15, 25, 20, 240), panel, border_radius=16)
        pygame.draw.rect(self.screen, (255, 215, 0), panel, 2, border_radius=16)
        txt = self.bg_f.render(msg, True, (255, 215, 0))
        self.screen.blit(txt, txt.get_rect(center=(panel.centerx, 180)))
        info_s = self.tl_f.render(f"{han}翻 {fu}符  合計 {cost}点", True, (255, 255, 255))
        self.screen.blit(info_s, info_s.get_rect(center=(panel.centerx, 245)))
        
        # 役一覧
        for i, y in enumerate(yaku_res[:12]):
            ja_n = YAKU_JA.get(y['name'], y['name'])
            name_s = self.ui_f.render(ja_n, True, (220, 220, 220))
            han_s = self.ui_f.render(f"{y['han']}翻", True, (255, 215, 0))
            y_pos = 295 + i * 30
            self.screen.blit(name_s, (panel.x + 140, y_pos))
            self.screen.blit(han_s, (panel.right - 180, y_pos))
            
        space_txt = self.ui_f.render("Spaceキーで次局へ", True, (255, 215, 0))
        self.screen.blit(space_txt, space_txt.get_rect(center=(panel.centerx, 690)))

