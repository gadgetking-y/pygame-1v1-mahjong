from mahjong.hand_calculating.hand import HandCalculator
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
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

    def to_34(self, ids, ms=[]):
        a = [0] * 34
        for tid in list(ids):
            if isinstance(tid, int): a[tid // 4] += 1
            else: a[tid] += 1
        for m in ms:
            a[m['ids'][0] // 4] += 3
        return a

    def get_shanten(self, h_ids, m_data=[]):
        try:
            return self.shanten_calc.calculate_shanten(self.to_34(h_ids, m_data))
        except:
            return 8

    def is_win(self, h_ids, m_data=[]):
        # 枚数チェック: 手牌 + 鳴き面子x3 = 14 (カンも1面子3枚として数える)
        h_len = len(h_ids)
        m_len = sum(3 for _ in m_data)
        if h_len + m_len != 14:
            return False
        
        c34 = self.to_34(h_ids, m_data)
        
        # 七対子判定 (鳴きがない場合のみ)
        if not m_data and sum(1 for c in c34 if c == 2) == 7:
            return True
        
        def check(arr):
            try:
                idx = next(i for i, c in enumerate(arr) if c > 0)
            except StopIteration:
                return True
            
            # 刻子として抜く
            if arr[idx] >= 3:
                nc = list(arr); nc[idx] -= 3
                if check(nc): return True
            
            # 順子として抜く
            if idx < 27 and idx % 9 <= 6:
                if arr[idx+1] > 0 and arr[idx+2] > 0:
                    nc = list(arr); nc[idx]-=1; nc[idx+1]-=1; nc[idx+2]-=1
                    if check(nc): return True
            return False

        # アタマを1つ決めて、残りが面子で構成できるか確認
        for i in range(34):
            if c34[i] >= 2:
                nc = list(c34); nc[i] -= 2
                if check(nc): return True
        return False

    def get_waiting_tiles_34(self, h_ids, m_data=[]):
        w = []
        for i in range(34):
            if self.is_win(list(h_ids) + [i * 4], m_data): w.append(i)
        return w

    def calculate_score(self, h_ids, win_id, melds_data, tsumo, riichi, dora_inds, is_dealer=False):
        ms = [Meld(Meld.KAN if len(m['ids'])==4 else Meld.PON, m['ids'], opened=m['opened']) for m in melds_data]
        rules = OptionalRules(has_open_tanyao=True, has_aka_dora=False)
        player_wind = 27 if is_dealer else 28
        config = HandConfig(is_tsumo=tsumo, is_riichi=riichi, player_wind=player_wind, round_wind=27, options=rules)
        try:
            return self.calculator.estimate_hand_value(h_ids, win_id, melds=ms, dora_indicators=dora_inds, config=config)
        except Exception as e:
            return type('Obj', (object,), {'error': str(e)})
