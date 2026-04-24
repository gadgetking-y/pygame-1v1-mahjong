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
        self.match_round, self.renchan, self.dealer, self.showing_final = 1, 0, "player", False
        self.reset_round()

    def reset_round(self):
        all_ids = [i for i in range(136) if not (4 <= i < 32)]; random.shuffle(all_ids)
        self.deck = all_ids; self.wall_idx, self.dora_count = 0, 1
        self.p_hand = sorted([self.draw_t_initial() for _ in range(13)])
        self.c_hand = sorted([self.draw_t_initial() for _ in range(13)])
        self.p_dis, self.c_dis, self.p_melds, self.c_melds = [], [], [], []
        self.state, self.current_turn = "DRAW", self.dealer
        self.drawn_t, self.last_dis = None, None
        self.p_riichi, self.c_riichi, self.riichi_pending = False, False, False
        self.p_ippatsu_pending, self.c_ippatsu_pending = False, False
        self.rinshan_turn = None
        self.draw_context = {"is_rinshan": False, "is_haitei": False}
        self.last_discard_context = {"is_houtei": False}
        self.msg, self.yaku_results, self.btns, self.timer = "", [], [], 0
        self.res_han, self.res_fu, self.res_cost = 0, 0, 0

    def draw_t_initial(self):
        t = self.deck[self.wall_idx]; self.wall_idx += 1; return t

    def draw_t(self):
        # 王牌残し
        if self.wall_idx < len(self.deck) - 14:
            t = self.deck[self.wall_idx]; self.wall_idx += 1; return t
        return None

    def is_furiten(self, hand, melds, discards):
        waiting_tiles_34 = self.logic.get_waiting_tiles_34(hand, melds)
        discarded_kinds = set(d['id'] // 4 for d in discards)
        for w in waiting_tiles_34:
            if w in discarded_kinds: return True
        return False

    def clear_ippatsu(self):
        self.p_ippatsu_pending, self.c_ippatsu_pending = False, False

    def get_win_context(self, winner, tsumo):
        ctx = {"is_ippatsu": self.p_ippatsu_pending if winner=="player" else self.c_ippatsu_pending}
        if tsumo:
            ctx["is_rinshan"] = self.draw_context.get("is_rinshan", False)
            ctx["is_haitei"] = self.draw_context.get("is_haitei", False)
            ctx["is_houtei"] = False
        else:
            ctx["is_rinshan"] = False
            ctx["is_haitei"] = False
            ctx["is_houtei"] = self.last_discard_context.get("is_houtei", False)
        return ctx

    def can_win(self, hand, win_tile, melds, tsumo, riichi, is_dealer, discards, win_context=None):
        """形だけでなく「役があるか」も事前に厳密にチェック"""
        if not tsumo and self.is_furiten(hand[:-1], melds, discards): return False
        di = self.logic.get_dora_indicators(self.deck, self.dora_count, riichi)
        res = self.logic.calculate_score(hand, win_tile, melds, tsumo, riichi, di, is_dealer, **(win_context or {}))
        return res is not None and getattr(res, 'error', None) is None

    def win(self, tsumo, winner):
        hand = list(self.p_hand if winner=="player" else self.c_hand)
        m = self.p_melds if winner=="player" else self.c_melds
        r = self.p_riichi if winner=="player" else self.c_riichi
        win_t = self.drawn_t if tsumo else self.last_dis
        di = self.logic.get_dora_indicators(self.deck, self.dora_count, r)
        res = self.logic.calculate_score(hand + [win_t], win_t, m, tsumo, r, di, winner==self.dealer, **self.get_win_context(winner, tsumo))
        
        if not res or getattr(res, 'error', None) is not None:
            err_msg = getattr(res, 'error', '役なし')
            self.msg = f"和了不可: {err_msg}"; self.yaku_results = []
            if winner != self.dealer: self.advance_round_logical()
        else:
            c = res.cost['total']; self.p_score += c if winner=="player" else -c; self.c_score += c if winner=="cpu" else -c
            self.msg = f"{winner.upper()} {'ツモ' if tsumo else 'ロン'}!"; self.res_han, self.res_fu, self.res_cost = res.han, res.fu, c
            self.yaku_results = []
            for y in res.yaku:
                h = getattr(y, 'han_closed', 0) if not m else getattr(y, 'han_open', 0)
                if h == 0: h = getattr(y, 'han', 1)
                self.yaku_results.append({'name': y.name, 'han': h})
            if winner == self.dealer: self.renchan += 1
            else: self.advance_round_logical()
        self.state = "END"

    def advance_round_logical(self):
        self.renchan = 0; self.dealer = "cpu" if self.dealer=="player" else "player"
        if self.dealer == "player": self.match_round += 1

    def discard(self, idx):
        if self.p_riichi and not self.riichi_pending: self.p_ippatsu_pending = False
        is_r = self.riichi_pending; t = self.drawn_t if idx == -1 else self.p_hand.pop(idx)
        if idx != -1 and self.drawn_t is not None: self.p_hand.append(self.drawn_t)
        self.p_hand = sorted(self.p_hand); self.p_dis.append({'id': t, 'horizontal': is_r}); self.last_dis, self.drawn_t = t, None
        self.last_discard_context = {"is_houtei": self.draw_context.get("is_haitei", False)}
        self.draw_context = {"is_rinshan": False, "is_haitei": False}
        if self.riichi_pending:
            self.p_riichi, self.p_score, self.riichi_pending, self.p_ippatsu_pending = True, self.p_score-1000, False, True
        self.current_turn, self.state = "cpu", "CHECK"

    def update(self):
        if self.showing_final: return
        now = pygame.time.get_ticks()
        if self.state == "DRAW":
            is_last_live_tile = self.wall_idx == len(self.deck) - 15
            t = self.draw_t()
            if t is None:
                self.draw_context = {"is_rinshan": False, "is_haitei": False}
                self.last_discard_context = {"is_houtei": False}
                self.msg, self.state = "流局", "END"
                if self.logic.is_win(self.p_hand, self.p_melds) or self.logic.is_win(self.c_hand, self.c_melds): self.renchan += 1
                else: self.advance_round_logical()
                return
            is_rinshan = self.rinshan_turn == self.current_turn
            self.draw_context = {"is_rinshan": is_rinshan, "is_haitei": is_last_live_tile and not is_rinshan}
            self.last_discard_context = {"is_houtei": False}
            self.rinshan_turn = None
            self.drawn_t, self.btns = t, []
            if self.current_turn == "player":
                # 枚数確認: 手牌 + 鳴き面子x3 = 13 (ツモ牌含まず、カンも1面子3枚換算)
                total = len(self.p_hand) + sum(3 for _ in self.p_melds)
                if total == 13:
                    if self.logic.is_win(self.p_hand + [t], self.p_melds):
                        if self.can_win(self.p_hand + [t], t, self.p_melds, True, self.p_riichi, self.dealer=="player", self.p_dis, self.get_win_context("player", True)):
                            self.btns.append({"text": "TSUMO", "rect": pygame.Rect(950, 600, 120, 50)})
                
                # 槓の判定 (リーチ中でも暗槓は可能だが、待ちが変わらない判定は簡易的に「リーチ前」のみ許可)
                kinds = [x//4 for x in self.p_hand]; t_kind = t//4
                if kinds.count(t_kind) == 3 and not self.p_riichi:
                    self.btns.append({"text": "KAN", "rect": pygame.Rect(950, 480, 120, 50)})
                
                if not self.p_riichi and not self.p_melds and self.logic.get_shanten(self.p_hand + [t]) <= 0:
                    self.btns.append({"text": "RIICHI", "rect": pygame.Rect(950, 540, 120, 50)})
                self.state = "WAIT" if not (self.p_riichi and not any(b["text"]=="TSUMO" for b in self.btns)) else "AUTO"
                if self.state == "AUTO": self.timer = now + 800
            else: self.timer, self.state = now + 1000, "CPU"
        elif self.state == "AUTO" and now > self.timer: self.discard(-1)
        elif self.state == "CPU" and now > self.timer:
            full = self.c_hand + [self.drawn_t]
            if self.logic.is_win(full, self.c_melds) and self.can_win(full, self.drawn_t, self.c_melds, True, self.c_riichi, self.dealer=="cpu", self.c_dis, self.get_win_context("cpu", True)): self.win(True, "cpu")
            else:
                bt, ms = full[0], 10
                for tx in full:
                    tmp = [x for x in full if x != tx]; s = self.logic.get_shanten(tmp, self.c_melds)
                    if s < ms: ms, bt = s, tx
                full.remove(bt); self.c_hand = sorted(full); self.drawn_t, is_h = None, False
                if self.c_riichi: self.c_ippatsu_pending = False
                if not self.c_riichi and ms <= 0 and not self.c_melds:
                    self.c_riichi, self.c_score, is_h, self.c_ippatsu_pending = True, self.c_score-1000, True, True
                self.c_dis.append({'id': bt, 'horizontal': is_h}); self.last_dis = bt; self.current_turn, self.state = "player", "CHECK"
                self.last_discard_context = {"is_houtei": self.draw_context.get("is_haitei", False)}
                self.draw_context = {"is_rinshan": False, "is_haitei": False}
        elif self.state == "CHECK":
            if self.current_turn == "player":
                if self.logic.is_win(self.p_hand + [self.last_dis], self.p_melds):
                    if self.can_win(self.p_hand + [self.last_dis], self.last_dis, self.p_melds, False, self.p_riichi, self.dealer=="player", self.p_dis, self.get_win_context("player", False)):
                        self.btns = [{"text": "RON", "rect": pygame.Rect(540, 450, 100, 50)}, {"text": "PASS", "rect": pygame.Rect(650, 450, 100, 50)}]
                    else: self.state = "DRAW"
                elif not self.p_riichi:
                    c = [tid//4 for tid in self.p_hand].count(self.last_dis//4)
                    if c >= 2: self.btns = [{"text": "KAN" if c==3 else "PON", "rect": pygame.Rect(540, 450, 100, 50)}, {"text": "PASS", "rect": pygame.Rect(650, 450, 100, 50)}]
                    else: self.state = "DRAW"
                else: self.state = "DRAW"
            else:
                if self.logic.is_win(self.c_hand + [self.last_dis], self.c_melds) and self.can_win(self.c_hand + [self.last_dis], self.last_dis, self.c_melds, False, self.c_riichi, self.dealer=="cpu", self.c_dis, self.get_win_context("cpu", False)): self.win(False, "cpu")
                else: self.state = "DRAW"

    def draw(self):
        self.screen.fill(COLOR_TABLE)
        pygame.draw.rect(self.screen, (0,0,0,100), (20, 20, 150, 300), border_radius=8)
        self.screen.blit(self.drawer.ui_f.render(f"東{self.match_round}局", True, COLOR_GOLD), (35, 210))
        if self.renchan > 0: self.screen.blit(self.drawer.ui_f.render(f"{self.renchan}本場", True, COLOR_WHITE), (35, 235))
        rem = len(self.deck)-14-self.wall_idx; self.screen.blit(self.drawer.ui_f.render(f"残り: {max(0, rem)}", True, COLOR_GOLD), (35, 260))
        di = self.logic.get_dora_indicators(self.deck, self.dora_count, (self.state=="END" and (self.p_riichi or self.c_riichi)))
        for i, tid in enumerate(di): self.drawer.draw_t(40, 70 + i*80, self.logic.get_tile_str(tid))
        for i, tid in enumerate(self.c_hand): self.drawer.draw_t(200+i*56, 50, self.logic.get_tile_str(tid), back=(self.state!="END" and not self.showing_final))
        for i, tid in enumerate(self.p_hand): self.drawer.draw_t(200+i*56, HAND_Y, self.logic.get_tile_str(tid), highlight=(self.state=="WAIT" and not self.p_riichi))
        if self.drawn_t is not None and self.current_turn=="player": self.drawer.draw_t(200+len(self.p_hand)*56+25, HAND_Y, self.logic.get_tile_str(self.drawn_t))
        for i, m in enumerate(self.p_melds):
            for j, tid in enumerate(m['ids']): self.drawer.draw_t(1000 - i*180 + j*56, HAND_Y, self.logic.get_tile_str(tid))
        # 捨て牌レイアウト (重なり回避済み)
        for i, d in enumerate(self.p_dis): self.drawer.draw_t(350+(i%10)*60, 640-(i//10)*85, self.logic.get_tile_str(d['id']), horizontal=d['horizontal'])
        for i, d in enumerate(self.c_dis): self.drawer.draw_t(350+(i%10)*60, 140+(i//10)*85, self.logic.get_tile_str(d['id']), horizontal=d['horizontal'])
        if self.p_riichi: self.drawer.draw_riichi_stick(550, 650)
        if self.c_riichi: self.drawer.draw_riichi_stick(550, 130)
        pygame.draw.rect(self.screen, (0,0,0,150), (20, 450, 200, 150), border_radius=10)
        self.screen.blit(self.drawer.ui_f.render(f"YOU: {self.p_score}{'(親)' if self.dealer=='player' else ''}", True, COLOR_WHITE), (40, 480)); self.screen.blit(self.drawer.ui_f.render(f"CPU: {self.c_score}{'(親)' if self.dealer=='cpu' else ''}", True, COLOR_WHITE), (40, 530))
        for b in self.btns:
            pygame.draw.rect(self.screen, COLOR_GOLD if b["text"] in ["RON","TSUMO","RIICHI"] else COLOR_WHITE, b["rect"], border_radius=5)
            self.screen.blit(self.drawer.ui_f.render(b["text"], True, COLOR_BLACK), b["rect"].move(25, 12))
        if self.msg:
            if self.showing_final: self.draw_f_res()
            else: self.drawer.draw_msg(self.msg, self.yaku_results, self.res_han, self.res_fu, self.res_cost)
        pygame.display.flip()

    def draw_f_res(self):
        pygame.draw.rect(self.screen, (0,0,0,240), (200, 150, 800, 550), border_radius=20)
        t = self.drawer.bg_f.render("東風戦 最終結果", True, COLOR_GOLD); self.screen.blit(t, t.get_rect(center=(600, 250)))
        winner = "YOU" if self.p_score > self.c_score else "CPU"
        r_s = self.drawer.bg_f.render(f"優勝: {winner}!", True, COLOR_WHITE); self.screen.blit(r_s, r_s.get_rect(center=(600, 380)))
        s_s = self.drawer.tl_f.render(f"YOU: {self.p_score}  vs  CPU: {self.c_score}", True, COLOR_GOLD); self.screen.blit(s_s, s_s.get_rect(center=(600, 480)))
        self.screen.blit(self.drawer.ui_f.render("Spaceキーでリスタート", True, COLOR_WHITE), (450, 620))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos(); action_done = False
                    for b in self.btns:
                        if b["rect"].collidepoint(pos):
                            if b["text"] == "RON": self.win(False, "player")
                            elif b["text"] == "TSUMO": self.win(True, "player")
                            elif b["text"] == "PON":
                                self.clear_ippatsu()
                                t = self.last_dis
                                if self.drawn_t is not None: self.p_hand.append(self.drawn_t); self.drawn_t = None
                                targets = [x for x in list(self.p_hand) if x//4 == t//4][:2]
                                for x in targets: self.p_hand.remove(x)
                                if self.c_dis: self.c_dis.pop()
                                self.p_melds.append({'ids': [t] + targets, 'opened': True}); self.current_turn, self.state, self.btns = "player", "WAIT", []
                            elif b["text"] == "KAN":
                                self.clear_ippatsu()
                                is_m = (self.state == "CHECK"); t = self.last_dis if is_m else self.drawn_t
                                if is_m and self.drawn_t is not None: self.p_hand.append(self.drawn_t); self.drawn_t = None
                                ts = [x for x in list(self.p_hand) if x//4 == t//4]
                                if not is_m: ts = ts[:3]
                                for x in ts: self.p_hand.remove(x)
                                if is_m: self.c_dis.pop()
                                else: self.drawn_t = None
                                self.p_melds.append({'ids': [t] + ts, 'opened': is_m}); self.dora_count = min(5, self.dora_count+1); self.rinshan_turn, self.state = "player", "DRAW"
                            elif b["text"] == "RIICHI": self.riichi_pending, self.btns = True, []
                            elif b["text"] == "PASS": self.btns, self.state = [], "DRAW"
                            action_done = True; break
                    if not action_done and self.state == "WAIT" and self.current_turn == "player":
                        if self.p_riichi and not self.riichi_pending: continue
                        tc = False
                        for i in range(len(self.p_hand)):
                            if pygame.Rect(200+i*56, HAND_Y, 54, 72).collidepoint(pos): self.discard(i); tc = True; break
                        if not tc and self.drawn_t is not None and pygame.Rect(200+len(self.p_hand)*56+25, HAND_Y, 54, 72).collidepoint(pos): self.discard(-1)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.state == "END":
                    if self.showing_final: self.p_score, self.c_score, self.match_round, self.renchan, self.dealer, self.showing_final = 30000, 30000, 1, 0, "player", False; self.reset_round()
                    elif self.match_round > 4 or self.p_score < 0 or self.c_score < 0: self.showing_final = True
                    else: self.reset_round()
            self.update(); self.draw(); self.clock.tick(60)

if __name__ == "__main__": MahjongGame().run()
