# /// script
# dependencies = ["pygame", "mahjong"]
# ///
import pygame, sys, random, os
from constants import *
from logic import MahjongLogic
from assets import download_assets, UIDrawer

class MahjongGame:
    def __init__(self):
        pygame.init(); self.clock = pygame.time.Clock()
        download_assets(ASSETS_DIR)
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("本格二人麻雀")
        self.drawer = UIDrawer(self.screen, ASSETS_DIR, TILE_W, TILE_H)
        self.logic = MahjongLogic(); self.p_score, self.c_score = 30000, 30000
        self.reset_round()

    def reset_round(self):
        all_ids = [i for i in range(136) if not (4 <= i < 32)] # 2-player
        self.deck = all_ids; random.shuffle(self.deck)
        self.wall_idx, self.dora_count = 0, 1
        self.p_hand = sorted([self.draw_t() for _ in range(13)])
        self.c_hand = sorted([self.draw_t() for _ in range(13)])
        self.p_dis, self.c_dis, self.p_melds, self.c_melds = [], [], [], []
        self.state, self.current_turn = "DRAW", "player"
        self.drawn_t, self.last_dis = None, None
        self.p_riichi, self.c_riichi, self.riichi_pending = False, False, False
        self.msg, self.yaku_list, self.btns, self.timer = "", [], [], 0

    def draw_t(self):
        if self.wall_idx < len(self.deck) - 14:
            t = self.deck[self.wall_idx]; self.wall_idx += 1; return t
        return None

    def win(self, tsumo, winner):
        hand = list(self.p_hand if winner=="player" else self.c_hand)
        melds = self.p_melds if winner=="player" else self.c_melds
        riichi = self.p_riichi if winner=="player" else self.c_riichi
        win_tile = self.drawn_t if tsumo else self.last_dis
        di = self.logic.get_dora_indicators(self.deck, self.dora_count, riichi)
        res = self.logic.calculate_score(hand + [win_tile], win_tile, melds, tsumo, riichi, di)
        if not res: self.msg = "和了エラー"
        else:
            c = res.cost['total']; self.p_score += c if winner=="player" else -c; self.c_score += c if winner=="cpu" else -c
            self.msg = f"{winner.upper()} {'ツモ' if tsumo else 'ロン'}! {c}点"; self.yaku_list = [y.name for y in res.yaku]
        self.state = "END"

    def discard(self, idx):
        t = self.drawn_t if idx == -1 else self.p_hand.pop(idx)
        if idx != -1 and self.drawn_t is not None: self.p_hand.append(self.drawn_t)
        self.p_hand = sorted(self.p_hand); self.p_dis.append(t); self.last_dis, self.drawn_t = t, None
        if self.riichi_pending: self.p_riichi, self.p_score, self.riichi_pending = True, self.p_score-1000, False
        self.current_turn, self.state = "cpu", "CHECK"

    def update(self):
        now = pygame.time.get_ticks()
        if self.state == "DRAW":
            t = self.draw_t()
            if not t: self.msg, self.state = "流局", "END"; return
            self.drawn_t, self.btns = t, []
            if self.current_turn == "player":
                if self.logic.is_win(self.p_hand + [t], self.p_melds):
                    self.btns.append({"text": "TSUMO", "rect": pygame.Rect(950, 600, 120, 50)})
                if self.p_hand.count(t) == 3 and not self.p_riichi:
                    self.btns.append({"text": "KAN", "rect": pygame.Rect(950, 480, 120, 50)})
                if not self.p_riichi and not self.p_melds and self.logic.get_shanten(self.p_hand + [t]) <= 0:
                    self.btns.append({"text": "RIICHI", "rect": pygame.Rect(950, 540, 120, 50)})
                self.state = "WAIT" if not (self.p_riichi and not any(b["text"]=="TSUMO" for b in self.btns)) else "AUTO"
                if self.state == "AUTO": self.timer = now + 800
            else: self.timer, self.state = now + 1000, "CPU"
        elif self.state == "AUTO" and now > self.timer: self.discard(-1)
        elif self.state == "CPU" and now > self.timer:
            full = self.c_hand + [self.drawn_t]
            if self.logic.is_win(full, self.c_melds): self.win(True, "cpu")
            else:
                bt, ms = full[0], 10
                for t in full:
                    tmp = [x for x in full if x != t]; s = self.logic.get_shanten(tmp, self.c_melds)
                    if s < ms: ms, bt = s, t
                full.remove(bt); self.c_hand = sorted(full); self.c_dis.append(bt); self.last_dis, self.drawn_t = bt, None
                self.current_turn, self.state = "player", "CHECK"
        elif self.state == "CHECK":
            if self.current_turn == "player":
                if self.logic.is_win(self.p_hand + [self.last_dis], self.p_melds):
                    self.btns = [{"text": "RON", "rect": pygame.Rect(540, 450, 100, 50)}, {"text": "PASS", "rect": pygame.Rect(650, 450, 100, 50)}]
                elif not self.p_riichi:
                    tp = [tid // 4 for tid in self.p_hand]; ldp = self.last_dis // 4; c = tp.count(ldp)
                    if c >= 2: self.btns = [{"text": "KAN" if c==3 else "PON", "rect": pygame.Rect(540, 450, 100, 50)}, {"text": "PASS", "rect": pygame.Rect(650, 450, 100, 50)}]
                    else: self.state = "DRAW"
                else: self.state = "DRAW"
            else:
                if self.logic.is_win(self.c_hand + [self.last_dis], self.c_melds): self.win(False, "cpu")
                else: self.state = "DRAW"

    def draw(self):
        self.screen.fill(COLOR_TABLE)
        pygame.draw.rect(self.screen, (0,0,0,100), (20, 20, 100, 200), border_radius=8)
        di = self.logic.get_dora_indicators(self.deck, self.dora_count, (self.state=="END" and (self.p_riichi or self.c_riichi)))
        for i, tid in enumerate(di): self.drawer.draw_t(40, 70 + i*80, self.logic.get_tile_str(tid))
        for i, tid in enumerate(self.c_hand): self.drawer.draw_t(200 + i * 56, 50, self.logic.get_tile_str(tid), back=(self.state!="END"))
        for i, tid in enumerate(self.p_hand): self.drawer.draw_t(200 + i * 56, 740, self.logic.get_tile_str(tid), highlight=(self.state=="WAIT" and not self.p_riichi))
        if self.drawn_t is not None and self.current_turn=="player": self.drawer.draw_t(200 + len(self.p_hand)*56+25, 740, self.logic.get_tile_str(self.drawn_t))
        for i, m in enumerate(self.p_melds):
            for j, tid in enumerate(m): self.drawer.draw_t(1000 - i*180 + j*56, 740, self.logic.get_tile_str(tid))
        for i, tid in enumerate(self.p_dis): self.drawer.draw_t(450 + (i%6)*56, 420 + (i//6)*72, self.logic.get_tile_str(tid))
        for i, tid in enumerate(self.c_dis): self.drawer.draw_t(450 + (i%6)*56, 330 - (i//6)*72, self.logic.get_tile_str(tid))
        pygame.draw.rect(self.screen, (0,0,0,150), (20, 450, 200, 150), border_radius=10)
        self.screen.blit(self.drawer.ui_f.render(f"YOU: {self.p_score}", True, COLOR_WHITE), (40, 480)); self.screen.blit(self.drawer.ui_f.render(f"CPU: {self.c_score}", True, COLOR_WHITE), (40, 530))
        for b in self.btns:
            pygame.draw.rect(self.screen, COLOR_GOLD if b["text"] in ["RON","TSUMO","RIICHI"] else COLOR_WHITE, b["rect"], border_radius=5)
            self.screen.blit(self.drawer.ui_f.render(b["text"], True, COLOR_BLACK), b["rect"].move(25, 12))
        if self.msg: self.drawer.draw_msg(self.msg, self.yaku_list)
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos(); action_done = False
                for b in self.btns:
                    if b["rect"].collidepoint(pos):
                        if b["text"] == "RON": self.win(False, "player")
                        elif b["text"] == "TSUMO": self.win(True, "player")
                        elif b["text"] == "PON":
                            t = self.last_dis; targets = [x for x in self.p_hand if x//4 == t//4][:2]
                            for x in targets: self.p_hand.remove(x)
                            if self.c_dis: self.c_dis.pop()
                            self.p_melds.append([t] + targets); self.current_turn, self.state, self.btns = "player", "WAIT", []
                        elif b["text"] == "KAN":
                            is_m = (self.state == "CHECK"); t = self.last_dis if is_m else self.drawn_t
                            targets = [x for x in list(self.p_hand) if x//4 == t//4]
                            for x in targets: self.p_hand.remove(x)
                            if is_m and self.c_dis: self.c_dis.pop()
                            self.p_melds.append([t] + targets); self.dora_count = min(5, self.dora_count+1); self.state = "DRAW"
                        elif b["text"] == "RIICHI": self.riichi_pending, self.btns = True, []
                        elif b["text"] == "PASS": self.btns, self.state = [], "DRAW"
                        action_done = True; break
                if not action_done and self.state == "WAIT" and self.current_turn == "player":
                    if self.p_riichi and not self.riichi_pending: continue
                    tc = False
                    for i in range(len(self.p_hand)):
                        if pygame.Rect(HAND_X+i*SPACING, HAND_Y, TILE_W, TILE_H).collidepoint(pos):
                            self.discard(i); tc = True; break
                    if not tc and self.drawn_t is not None and pygame.Rect(HAND_X+len(self.p_hand)*SPACING+GAP, HAND_Y, TILE_W, TILE_H).collidepoint(pos): self.discard(-1)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.state == "END": self.reset_round()

    def run(self):
        while True:
            self.handle_events(); self.update(); self.draw(); self.clock.tick(FPS)

if __name__ == "__main__":
    MahjongGame().run()
