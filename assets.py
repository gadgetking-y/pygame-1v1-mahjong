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
        self.screen = screen; self.imgs = {}
        for k, f in IMAGE_FN.items():
            p = os.path.join(assets_dir, f)
            if os.path.exists(p): self.imgs[k] = pygame.transform.smoothscale(pygame.image.load(p).convert_alpha(), (w, h))
        ja_f = ["hiraginosansgbw3", "msgothic", "stheitimedium", "arialunicode", "applesdgothicneo", "notosanscjkjp"]
        fn = next((f for f in ja_f if f in pygame.font.get_fonts()), None)
        self.ui_f = pygame.font.SysFont(fn, 24)
        self.tl_f = pygame.font.SysFont(fn, 32, bold=True)
        self.bg_f = pygame.font.SysFont(fn, 60, bold=True)

    def draw_t(self, x, y, name, back=False, highlight=False):
        rect = pygame.Rect(x, y, 54, 72)
        pygame.draw.rect(self.screen, (20,60,20), rect.move(3,3), border_radius=4)
        pygame.draw.rect(self.screen, (255,255,250) if not back else (255,120,0), rect, border_radius=4)
        img = self.imgs.get("Back" if back else (name or "Front"))
        if img: self.screen.blit(img, (x, y))
        elif not back and name:
            s = self.tl_f.render(name, True, (0,0,0))
            self.screen.blit(s, s.get_rect(center=rect.center))
        pygame.draw.rect(self.screen, (0,0,0), rect, 1, border_radius=4)
        if highlight: pygame.draw.rect(self.screen, (255,215,0), rect, 3, border_radius=4)

    def draw_msg(self, msg, yaku_res, han, fu, cost):
        pygame.draw.rect(self.screen, (0,0,0,230), (250,100,700,650), border_radius=15)
        pygame.draw.rect(self.screen, (255,215,0), (250,100,700,650), 2, border_radius=15)
        txt = self.bg_f.render(msg, True, (255,215,0))
        self.screen.blit(txt, txt.get_rect(center=(600, 180)))
        info_s = self.tl_f.render(f"{han}翻 {fu}符  合計 {cost}点", True, (255,255,255))
        self.screen.blit(info_s, info_s.get_rect(center=(600, 250)))
        for i, y in enumerate(yaku_res[:12]):
            name = YAKU_JA.get(y['name'], y['name'])
            n_s = self.ui_f.render(name, True, (220,220,220))
            h_s = self.ui_f.render(f"{y['han']}翻", True, (255,255,250))
            self.screen.blit(n_s, (400, 300 + i*32)); self.screen.blit(h_s, (750, 300 + i*32))
        self.screen.blit(self.ui_f.render("Spaceキーで次局へ", True, (255,215,0)), (500, 700))
