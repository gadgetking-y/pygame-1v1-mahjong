# /// script
# dependencies = ["pygame", "mahjong"]
# ///
import pygame, sys, random, os, math, array
from constants import *
from logic import MahjongLogic
from assets import download_assets, UIDrawer

class MahjongGame:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init(); self.clock = pygame.time.Clock()
        download_assets(ASSETS_DIR)
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("本格二人麻雀")
        self.drawer = UIDrawer(self.screen, ASSETS_DIR, TILE_W, TILE_H)
        self.sounds = self.setup_sounds()
        self.sound_enabled = True
        self.logic = MahjongLogic(); self.p_score, self.c_score = 30000, 30000
        self.match_round, self.renchan, self.dealer, self.showing_final = 1, 0, "player", False
        self.reset_round()

    def setup_sounds(self):
        if not pygame.mixer.get_init(): return {}

        def tone(freqs, duration=0.08, volume=0.25):
            rate = 44100
            samples = array.array("h")
            total = max(1, int(rate * duration))
            for i in range(total):
                t = i / rate
                decay = 1 - (i / total)
                value = sum(math.sin(2 * math.pi * f * t) for f in freqs) / len(freqs)
                samples.append(int(32767 * volume * decay * value))
            return pygame.mixer.Sound(buffer=samples.tobytes())

        try:
            return {
                "tile": tone([620, 900], 0.045, 0.18),
                "call": tone([420, 630], 0.09, 0.22),
                "riichi": tone([720, 960, 1200], 0.12, 0.2),
                "win": tone([520, 780, 1040], 0.28, 0.24),
            }
        except pygame.error:
            return {}

    def play_sound(self, name):
        if not self.sound_enabled: return
        sound = self.sounds.get(name)
        if sound: sound.play()

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled

    def add_effect(self, text, x, y, color=COLOR_GOLD, duration=650, size="title"):
        self.effects.append({"text": text, "x": x, "y": y, "color": color, "start": pygame.time.get_ticks(), "duration": duration, "size": size})

    def reset_round(self):
        all_ids = list(range(136)); random.shuffle(all_ids)
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
        self.effects = []

    def draw_t_initial(self):
        t = self.deck[self.wall_idx]; self.wall_idx += 1; return t

    def draw_t(self):
        # 王牌残し
        if self.wall_idx < len(self.deck) - 14:
            t = self.deck[self.wall_idx]; self.wall_idx += 1; return t
        return None

    def get_layout(self):
        side_rect = pygame.Rect(28, 28, 280, 794)
        action_x = SCREEN_W - 180
        play_left = side_rect.right + 32
        play_right = action_x - 30
        play_center_x = (play_left + play_right) // 2
        discard_cols = 10
        discard_step_x, discard_step_y = TILE_W + 4, TILE_H + 4
        river_width = 10 * discard_step_x + 20 # 10枚並び（横向き牌考慮の余裕）
        river_x = play_center_x - river_width // 2
        hand_width = 13 * SPACING + GAP + TILE_W
        return {
            "side_rect": side_rect,
            "info_rect": pygame.Rect(side_rect.x + 14, side_rect.y + 14, side_rect.width - 28, 170),
            "dora_rect": pygame.Rect(side_rect.x + 14, side_rect.y + 200, side_rect.width - 28, 110),
            "score_rect": pygame.Rect(side_rect.x + 14, side_rect.y + 326, side_rect.width - 28, 380),
            "sound_rect": pygame.Rect(side_rect.x + 30, side_rect.y + 724, side_rect.width - 60, 40),
            "action_x": action_x,
            "play_left": play_left,
            "play_right": play_right,
            "discard_cols": discard_cols,
            "discard_step_x": discard_step_x,
            "discard_step_y": discard_step_y,
            "river_x": river_x,
            "river_width": river_width,
            "cpu_hand_y": 45,
            "cpu_river_y": 160,
            "player_river_y": 540,
            "hand_x": play_center_x - hand_width // 2,
            "meld_x": play_right - 180,
            "riichi_x": play_center_x - 55,
        }


    def get_action_button_rect(self, slot, y, width=120, height=50):
        gap = 12
        x = SCREEN_W - 60 - width - slot * (width + gap)
        return pygame.Rect(x, y, width, height)

    def get_dora_pos(self, index):
        layout = self.get_layout()
        d_rect = layout["dora_rect"]
        scale = 0.78
        w = int(TILE_W * scale)
        step_x = w + 4
        start_x = d_rect.centerx - (5 * step_x) // 2
        start_y = d_rect.y + 45
        return start_x + index * step_x, start_y

    def get_discard_pos(self, index, is_player):
        layout = self.get_layout()
        col, row = index % layout["discard_cols"], index // layout["discard_cols"]
        y = layout["player_river_y"] - row * layout["discard_step_y"] if is_player else layout["cpu_river_y"] + row * layout["discard_step_y"]
        # 概算X位置（エフェクト表示用）
        return layout["river_x"] + col * layout["discard_step_x"], y


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
            self.play_sound("win")
            self.add_effect("ツモ" if tsumo else "ロン", SCREEN_W // 2, SCREEN_H // 2 - 80, COLOR_GOLD, 1000)
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
        dx, dy = self.get_discard_pos(len(self.p_dis) - 1, True)
        self.play_sound("riichi" if is_r else "tile")
        self.add_effect("リーチ" if is_r else "打牌", dx + TILE_W // 2, dy - 8, COLOR_GOLD if is_r else COLOR_WHITE, 700, "small")
        self.last_discard_context = {"is_houtei": self.draw_context.get("is_haitei", False)}
        self.draw_context = {"is_rinshan": False, "is_haitei": False}
        if self.riichi_pending:
            self.p_riichi, self.p_score, self.riichi_pending, self.p_ippatsu_pending = True, self.p_score-1000, False, True
        self.current_turn, self.state = "cpu", "CHECK"

    def draw_effects(self):
        now = pygame.time.get_ticks()
        alive = []
        for effect in self.effects:
            progress = (now - effect["start"]) / effect["duration"]
            if progress >= 1: continue
            alive.append(effect)
            alpha = max(0, min(255, int(255 * (1 - progress))))
            y = effect["y"] - int(28 * progress)
            font = self.drawer.tl_f if effect["size"] == "small" else self.drawer.bg_f
            text = font.render(effect["text"], True, effect["color"])
            text.set_alpha(alpha)
            rect = text.get_rect(center=(effect["x"], y))
            glow = pygame.Surface((rect.width + 24, rect.height + 16), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*effect["color"], max(0, alpha // 5)), glow.get_rect(), border_radius=8)
            self.screen.blit(glow, glow.get_rect(center=rect.center))
            self.screen.blit(text, rect)
        self.effects = alive

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
                            self.btns.append({"text": "TSUMO", "rect": self.get_action_button_rect(0, 600)})
                
                # 槓の判定 (リーチ中でも暗槓は可能だが、待ちが変わらない判定は簡易的に「リーチ前」のみ許可)
                kinds = [x//4 for x in self.p_hand]; t_kind = t//4
                if kinds.count(t_kind) == 3 and not self.p_riichi:
                    self.btns.append({"text": "KAN", "rect": self.get_action_button_rect(0, 480)})
                
                if not self.p_riichi and not self.p_melds and self.logic.get_shanten(self.p_hand + [t]) <= 0:
                    self.btns.append({"text": "RIICHI", "rect": self.get_action_button_rect(0, 540)})
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
                dx, dy = self.get_discard_pos(len(self.c_dis) - 1, False)
                self.play_sound("riichi" if is_h else "tile")
                self.add_effect("リーチ" if is_h else "打牌", dx + TILE_W // 2, dy + TILE_H + 8, COLOR_GOLD if is_h else COLOR_WHITE, 700, "small")
                self.last_discard_context = {"is_houtei": self.draw_context.get("is_haitei", False)}
                self.draw_context = {"is_rinshan": False, "is_haitei": False}
        elif self.state == "CHECK":
            if self.current_turn == "player":
                if self.logic.is_win(self.p_hand + [self.last_dis], self.p_melds):
                    if self.can_win(self.p_hand + [self.last_dis], self.last_dis, self.p_melds, False, self.p_riichi, self.dealer=="player", self.p_dis, self.get_win_context("player", False)):
                        self.btns = [{"text": "RON", "rect": self.get_action_button_rect(1, 450, 100)}, {"text": "PASS", "rect": self.get_action_button_rect(0, 450, 100)}]
                    else: self.state = "DRAW"
                elif not self.p_riichi:
                    c = [tid//4 for tid in self.p_hand].count(self.last_dis//4)
                    if c >= 2: self.btns = [{"text": "KAN" if c==3 else "PON", "rect": self.get_action_button_rect(1, 450, 100)}, {"text": "PASS", "rect": self.get_action_button_rect(0, 450, 100)}]
                    else: self.state = "DRAW"
                else: self.state = "DRAW"
            else:
                if self.logic.is_win(self.c_hand + [self.last_dis], self.c_melds) and self.can_win(self.c_hand + [self.last_dis], self.last_dis, self.c_melds, False, self.c_riichi, self.dealer=="cpu", self.c_dis, self.get_win_context("cpu", False)): self.win(False, "cpu")
                else: self.state = "DRAW"

    def draw(self):
        layout = self.get_layout()
        self.screen.fill(COLOR_TABLE)
        
        # 外枠ラグジュアリーフレーム
        pygame.draw.rect(self.screen, COLOR_TABLE_BORDER, (0, 0, SCREEN_W, SCREEN_H), 8)
        
        # --- 左サイドパネル ---
        side = layout["side_rect"]
        pygame.draw.rect(self.screen, (12, 28, 18), side, border_radius=16)
        pygame.draw.rect(self.screen, (40, 90, 55), side, 2, border_radius=16)
        
        # 1. 卓情報
        info = layout["info_rect"]
        pygame.draw.rect(self.screen, (20, 45, 30), info, border_radius=10)
        self.screen.blit(self.drawer.tl_f.render("対局情報", True, COLOR_GOLD), (info.x + 16, info.y + 14))
        self.screen.blit(self.drawer.ui_f.render(f"東{self.match_round}局  {self.renchan}本場", True, COLOR_WHITE), (info.x + 16, info.y + 58))
        rem = max(0, len(self.deck) - 14 - self.wall_idx)
        self.screen.blit(self.drawer.ui_f.render(f"残り山牌: {rem}枚", True, COLOR_CYAN), (info.x + 16, info.y + 104))
        
        # 2. ドラ表示エリア（王牌5枚）
        dora_r = layout["dora_rect"]
        pygame.draw.rect(self.screen, (20, 45, 30), dora_r, border_radius=10)
        self.screen.blit(self.drawer.ui_f.render("ドラ表示牌", True, COLOR_GOLD), (dora_r.x + 14, dora_r.y + 10))
        di = self.logic.get_dora_indicators(self.deck, self.dora_count, (self.state=="END" and (self.p_riichi or self.c_riichi)))
        # 5枚分（ドラ表示牌 + 未めくりの王牌）
        for i in range(5):
            x, y = self.get_dora_pos(i)
            if i < len(di):
                self.drawer.draw_t(x, y, self.logic.get_tile_str(di[i]), scale=0.78)
            else:
                self.drawer.draw_t(x, y, "", back=True, scale=0.78)
                
        # 3. スコア・対戦者情報
        score_r = layout["score_rect"]
        pygame.draw.rect(self.screen, (20, 45, 30), score_r, border_radius=10)
        self.screen.blit(self.drawer.tl_f.render("対局者スコア", True, COLOR_GOLD), (score_r.x + 16, score_r.y + 16))
        
        # CPU スコアプレート
        cpu_box = pygame.Rect(score_r.x + 12, score_r.y + 60, score_r.width - 24, 110)
        pygame.draw.rect(self.screen, (15, 35, 24), cpu_box, border_radius=8)
        self.screen.blit(self.drawer.ui_f.render("CPU", True, (200, 220, 210)), (cpu_box.x + 14, cpu_box.y + 16))
        if self.dealer == "cpu":
            dealer_badge = pygame.Rect(cpu_box.right - 54, cpu_box.y + 14, 40, 24)
            pygame.draw.rect(self.screen, COLOR_GOLD, dealer_badge, border_radius=6)
            txt_parent = self.drawer.sm_f.render("親", True, COLOR_BLACK)
            self.screen.blit(txt_parent, txt_parent.get_rect(center=dealer_badge.center))
        self.screen.blit(self.drawer.tl_f.render(f"{self.c_score} 点", True, COLOR_WHITE), (cpu_box.x + 14, cpu_box.y + 54))

        # YOU スコアプレート
        you_box = pygame.Rect(score_r.x + 12, score_r.y + 190, score_r.width - 24, 110)
        pygame.draw.rect(self.screen, (15, 35, 24), you_box, border_radius=8)
        self.screen.blit(self.drawer.ui_f.render("YOU (あなた)", True, COLOR_GOLD), (you_box.x + 14, you_box.y + 16))
        if self.dealer == "player":
            dealer_badge = pygame.Rect(you_box.right - 54, you_box.y + 14, 40, 24)
            pygame.draw.rect(self.screen, COLOR_GOLD, dealer_badge, border_radius=6)
            txt_parent = self.drawer.sm_f.render("親", True, COLOR_BLACK)
            self.screen.blit(txt_parent, txt_parent.get_rect(center=dealer_badge.center))
        self.screen.blit(self.drawer.tl_f.render(f"{self.p_score} 点", True, COLOR_WHITE), (you_box.x + 14, you_box.y + 54))


        # SOUNDボタン
        sound_r = layout["sound_rect"]
        sound_bg = (40, 120, 70) if self.sound_enabled else (60, 70, 65)
        pygame.draw.rect(self.screen, sound_bg, sound_r, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_GOLD if self.sound_enabled else (120,120,120), sound_r, 1, border_radius=8)
        sound_label = "🔊 SOUND ON" if self.sound_enabled else "🔇 SOUND OFF"
        self.screen.blit(self.drawer.ui_f.render(sound_label, True, COLOR_WHITE), sound_r.move(25, 8))

        # --- 中央河（卓の中央エリア） ---
        center_x = (layout["play_left"] + layout["play_right"]) // 2
        center_rect = pygame.Rect(center_x - 290, 130, 580, 500)
        pygame.draw.rect(self.screen, (16, 75, 40), center_rect, border_radius=16)
        pygame.draw.rect(self.screen, (70, 140, 95), center_rect, 2, border_radius=16)
        
        # 中央仕切り線（CPU河とPlayer河を隔てる正確な中央線）
        mid_y = 382
        pygame.draw.line(self.screen, (50, 110, 75), (center_rect.x + 20, mid_y), (center_rect.right - 20, mid_y), 2)

        # --- 手牌と鳴き牌 ---
        # CPU手牌
        for i, tid in enumerate(self.c_hand):
            self.drawer.draw_t(layout["hand_x"] + i * SPACING, layout["cpu_hand_y"], self.logic.get_tile_str(tid), back=(self.state!="END" and not self.showing_final))
        # Player手牌
        for i, tid in enumerate(self.p_hand):
            self.drawer.draw_t(layout["hand_x"] + i * SPACING, HAND_Y, self.logic.get_tile_str(tid), highlight=(self.state=="WAIT" and not self.p_riichi))
        if self.drawn_t is not None and self.current_turn=="player":
            self.drawer.draw_t(layout["hand_x"] + len(self.p_hand) * SPACING + GAP, HAND_Y, self.logic.get_tile_str(self.drawn_t))
        # Player副露
        for i, m in enumerate(self.p_melds):
            for j, tid in enumerate(m['ids']):
                self.drawer.draw_t(layout["meld_x"] - i * 170 + j * (SPACING - 4), HAND_Y, self.logic.get_tile_str(tid))

        # --- 河（捨て牌）の描画 ---
        # 1行10枚で累積X座標計算を行い、二人麻雀の大盛り捨て牌も美しく並べる
        def draw_river_discards(discards, is_player):
            cols = layout["discard_cols"]
            max_rows = max(3, math.ceil(len(discards) / cols))
            for row_idx in range(max_rows):
                row_discards = discards[row_idx * cols : (row_idx + 1) * cols]
                if not row_discards: continue
                
                # 行ごとのY座標
                base_y = layout["player_river_y"] - row_idx * layout["discard_step_y"] if is_player else layout["cpu_river_y"] + row_idx * layout["discard_step_y"]
                cur_x = layout["river_x"]
                
                for d in row_discards:
                    is_h = d['horizontal']
                    # 横向き時はY位置を中央寄せ調整
                    tile_y = base_y + (TILE_H - TILE_W) // 2 if is_h else base_y
                    self.drawer.draw_t(cur_x, tile_y, self.logic.get_tile_str(d['id']), horizontal=is_h)
                    cur_x += (TILE_H + 4) if is_h else (TILE_W + 4)

        draw_river_discards(self.c_dis, False)
        draw_river_discards(self.p_dis, True)


        # --- リーチ棒 ---
        if self.p_riichi:
            self.drawer.draw_riichi_stick(layout["riichi_x"], layout["player_river_y"] + TILE_H + 12)
        if self.c_riichi:
            self.drawer.draw_riichi_stick(layout["riichi_x"], layout["cpu_river_y"] - 24)

        # --- アクションボタン ---
        for b in self.btns:
            btn_col = COLOR_GOLD if b["text"] in ["RON","TSUMO","RIICHI"] else (240, 240, 240)
            pygame.draw.rect(self.screen, btn_col, b["rect"], border_radius=8)
            pygame.draw.rect(self.screen, (40,40,40), b["rect"], 1, border_radius=8)
            txt_s = self.drawer.tl_f.render(b["text"], True, COLOR_BLACK)
            self.screen.blit(txt_s, txt_s.get_rect(center=b["rect"].center))

        if self.msg:
            if self.showing_final: self.draw_f_res()
            else: self.drawer.draw_msg(self.msg, self.yaku_results, self.res_han, self.res_fu, self.res_cost)
        self.draw_effects()
        pygame.display.flip()


    def draw_f_res(self):
        panel = pygame.Rect((SCREEN_W - 820) // 2, 150, 820, 550)
        pygame.draw.rect(self.screen, (0,0,0,240), panel, border_radius=20)
        t = self.drawer.bg_f.render("東風戦 最終結果", True, COLOR_GOLD); self.screen.blit(t, t.get_rect(center=(SCREEN_W // 2, 250)))
        winner = "YOU" if self.p_score > self.c_score else "CPU"
        r_s = self.drawer.bg_f.render(f"優勝: {winner}!", True, COLOR_WHITE); self.screen.blit(r_s, r_s.get_rect(center=(SCREEN_W // 2, 380)))
        s_s = self.drawer.tl_f.render(f"YOU: {self.p_score}  vs  CPU: {self.c_score}", True, COLOR_GOLD); self.screen.blit(s_s, s_s.get_rect(center=(SCREEN_W // 2, 480)))
        self.screen.blit(self.drawer.ui_f.render("Spaceキーでリスタート", True, COLOR_WHITE), (SCREEN_W // 2 - 100, 620))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos(); action_done = False
                    if self.get_layout()["sound_rect"].collidepoint(pos):
                        self.toggle_sound(); action_done = True
                    for b in self.btns:
                        if b["rect"].collidepoint(pos):
                            if b["text"] == "RON": self.win(False, "player")
                            elif b["text"] == "TSUMO": self.win(True, "player")
                            elif b["text"] == "PON":
                                self.clear_ippatsu()
                                self.play_sound("call"); self.add_effect("ポン", SCREEN_W // 2, SCREEN_H // 2, COLOR_GOLD, 750)
                                t = self.last_dis
                                if self.drawn_t is not None: self.p_hand.append(self.drawn_t); self.drawn_t = None
                                targets = [x for x in list(self.p_hand) if x//4 == t//4][:2]
                                for x in targets: self.p_hand.remove(x)
                                if self.c_dis: self.c_dis.pop()
                                self.p_melds.append({'ids': [t] + targets, 'opened': True}); self.current_turn, self.state, self.btns = "player", "WAIT", []
                            elif b["text"] == "KAN":
                                self.clear_ippatsu()
                                self.play_sound("call"); self.add_effect("カン", SCREEN_W // 2, SCREEN_H // 2, COLOR_GOLD, 750)
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
                        layout = self.get_layout()
                        tc = False
                        for i in range(len(self.p_hand)):
                            if pygame.Rect(layout["hand_x"] + i * SPACING, HAND_Y, TILE_W, TILE_H).collidepoint(pos): self.discard(i); tc = True; break
                        if not tc and self.drawn_t is not None and pygame.Rect(layout["hand_x"] + len(self.p_hand) * SPACING + GAP, HAND_Y, TILE_W, TILE_H).collidepoint(pos): self.discard(-1)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.state == "END":
                    if self.showing_final: self.p_score, self.c_score, self.match_round, self.renchan, self.dealer, self.showing_final = 30000, 30000, 1, 0, "player", False; self.reset_round()
                    elif self.match_round > 4 or self.p_score < 0 or self.c_score < 0: self.showing_final = True
                    else: self.reset_round()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                    self.toggle_sound()
            self.update(); self.draw(); self.clock.tick(60)

if __name__ == "__main__": MahjongGame().run()
