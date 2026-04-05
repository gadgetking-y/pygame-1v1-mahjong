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
        if tid < 36: return f"M{tid // 4 + 1}"
        if tid < 72: return f"P{(tid - 36) // 4 + 1}"
        if tid < 108: return f"S{(tid - 72) // 4 + 1}"
        return f"H{(tid - 108) // 4 + 1}"

    def get_dora_indicators(self, deck, count, include_ura=False):
        inds = [deck[-(5 + i*2)] for i in range(count)]
        if include_ura: inds += [deck[-(6 + i*2)] for i in range(count)]
        return inds

    def to_34(self, tile_ids, melds_data=[]):
        all_ids = list(tile_ids)
        for m in melds_data: all_ids.extend(m['ids'])
        arr = [0] * 34
        for tid in all_ids: arr[tid // 4] += 1
        return arr

    def get_shanten(self, h_ids, m_data=[]):
        try: return self.shanten_calc.calculate_shanten(self.to_34(h_ids, m_data))
        except: return 8

    def is_win(self, h_ids, m_data=[]):
        if len(h_ids) + sum(3 for _ in m_data) != 14: return False
        c34 = self.to_34(h_ids, m_data)
        if not m_data and sum(1 for c in c34 if c == 2) == 7: return True
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

    def calculate_score(self, h_ids, win_id, melds_data, tsumo, riichi, dora_inds):
        # melds_data: [{'ids': [id1, id2, id3], 'opened': True}, ...]
        ms = [Meld(Meld.KAN if len(m['ids'])==4 else Meld.PON, m['ids'], opened=m['opened']) for m in melds_data]
        config = HandConfig(is_tsumo=tsumo, is_riichi=riichi)
        try:
            # tilesには win_id も含めた「鳴いていない牌（closed_hand）」を渡す
            return self.calculator.estimate_hand_value(h_ids, win_id, melds=ms, dora_indicators=dora_inds, config=config)
        except Exception as e:
            print(f"Logic Error: {e}")
            return None
