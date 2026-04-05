from mahjong.hand_calculating.hand import HandCalculator
from mahjong.hand_calculating.hand_config import HandConfig
from mahjong.tile import TilesConverter
from mahjong.meld import Meld
from mahjong.shanten import Shanten

class MahjongLogic:
    def __init__(self):
        self.calculator = HandCalculator()
        self.shanten_calc = Shanten()

    @staticmethod
    def get_tile_str(tid):
        """物理ID(0-135)を名前(M1等)に変換"""
        if tid < 36: return f"M{tid // 4 + 1}"
        if tid < 72: return f"P{(tid - 36) // 4 + 1}"
        if tid < 108: return f"S{(tid - 72) // 4 + 1}"
        return f"H{(tid - 108) // 4 + 1}"

    def get_dora_indicators(self, deck, count, include_ura=False):
        # indicators are taken from the end of the shuffled deck
        inds = [deck[-(5 + i*2)] for i in range(count)]
        if include_ura:
            inds += [deck[-(6 + i*2)] for i in range(count)]
        return inds

    def to_34(self, ids, ms=[]):
        a = [0] * 34
        for tid in list(ids):
            a[tid // 4] += 1
        for m in ms:
            for tid in m:
                a[tid // 4] += 1
        return a

    def get_shanten(self, ids, ms=[]):
        try: return self.shanten_calc.calculate_shanten(self.to_34(ids, ms))
        except: return 8

    def is_win(self, ids, ms=[]):
        total_tiles = len(ids) + sum(3 for m in ms)
        if total_tiles != 14: return False
        
        c34 = self.to_34(ids, ms)
        # Seven pairs
        if not ms and sum(1 for c in c34 if c == 2) == 7: return True
        
        def check(arr):
            try: idx = next(i for i, c in enumerate(arr) if c > 0)
            except StopIteration: return True
            if arr[idx] >= 3:
                nc = list(arr); nc[idx] -= 3
                if check(nc): return True
            if idx < 27 and idx % 9 <= 6:
                if arr[idx+1] > 0 and arr[idx+2] > 0:
                    nc = list(arr); nc[idx]-=1; nc[idx+1]-=1; nc[idx+2]-=1
                    if check(nc): return True
            return False

        for i in range(34):
            if c34[i] >= 2:
                nc = list(c34); nc[i] -= 2
                if check(nc): return True
        return False

    def calculate_score(self, closed_ids, win_id, melds_ids, tsumo, riichi, dora_inds):
        # tiles: list of all 14 physical IDs (closed part only? No, all 14 according to library)
        # Actually, for the mahjong library:
        # - tiles: all 14 tiles if closed.
        # - if there are melds, tiles should be closed part + win_tile.
        # win_id: must be in tiles
        
        ms = [Meld(Meld.KAN if len(m)==4 else Meld.PON, m, opened=True) for m in melds_ids]
        config = HandConfig(is_tsumo=tsumo, is_riichi=riichi)
        try:
            res = self.calculator.estimate_hand_value(closed_ids, win_id, melds=ms, dora_indicators=dora_inds, config=config)
            return res
        except Exception as e:
            print(f"Logic Scoring Error: {e}")
            return None
