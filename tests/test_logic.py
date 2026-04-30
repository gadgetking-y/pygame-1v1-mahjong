from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from logic import MahjongLogic
from mahjong.tile import TilesConverter


def _pick_tile(tiles, tile_34):
    return next(tile for tile in tiles if tile // 4 == tile_34)


def test_rinshan_only_hand_is_scored():
    logic = MahjongLogic()
    closed_tiles = TilesConverter.string_to_136_array(man="11", pin="789", sou="123456")
    melds = [{"ids": TilesConverter.string_to_136_array(pin="2222"), "opened": True}]
    win_tile = _pick_tile(closed_tiles, 17)  # 9p

    no_context = logic.calculate_score(closed_tiles, win_tile, melds, True, False, [], False)
    assert getattr(no_context, "error", None) is not None

    res = logic.calculate_score(
        closed_tiles,
        win_tile,
        melds,
        True,
        False,
        [],
        False,
        is_rinshan=True,
    )

    assert getattr(res, "error", None) is None
    assert "Rinshan Kaihou" in [y.name for y in res.yaku]


def test_haitei_only_hand_is_scored():
    logic = MahjongLogic()
    closed_tiles = TilesConverter.string_to_136_array(man="11", pin="789", sou="123456")
    melds = [{"ids": TilesConverter.string_to_136_array(pin="222"), "opened": True}]
    win_tile = _pick_tile(closed_tiles, 17)  # 9p

    no_context = logic.calculate_score(closed_tiles, win_tile, melds, True, False, [], False)
    assert getattr(no_context, "error", None) is not None

    res = logic.calculate_score(
        closed_tiles,
        win_tile,
        melds,
        True,
        False,
        [],
        False,
        is_haitei=True,
    )

    assert getattr(res, "error", None) is None
    assert "Haitei Raoyue" in [y.name for y in res.yaku]


def test_houtei_only_hand_is_scored():
    logic = MahjongLogic()
    closed_tiles = TilesConverter.string_to_136_array(man="11", pin="789", sou="123456")
    melds = [{"ids": TilesConverter.string_to_136_array(pin="222"), "opened": True}]
    win_tile = _pick_tile(closed_tiles, 17)  # 9p

    no_context = logic.calculate_score(closed_tiles, win_tile, melds, False, False, [], False)
    assert getattr(no_context, "error", None) is not None

    res = logic.calculate_score(
        closed_tiles,
        win_tile,
        melds,
        False,
        False,
        [],
        False,
        is_houtei=True,
    )

    assert getattr(res, "error", None) is None
    assert "Houtei Raoyui" in [y.name for y in res.yaku]
