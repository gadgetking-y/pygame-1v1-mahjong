# 1v1 Riichi Mahjong (本格二人麻雀)

A full-featured 1v1 Riichi Mahjong game built with Pygame. Features smooth scaling, realistic tile graphics, accurate yaku calculation, and a modernized board UI.

## Features

- **Sleek Modern Graphics**: High-quality tile assets automatically downloaded, framed in a luxury green-felt table design.
- **Optimized Layout**: Wide discard river tailored for 1v1 play, dedicated Dora indicator panel, clean dealer badges, and 3D-styled Riichi sticks.
- **Full Rule Implementation**: Supports Riichi, Pon, Kan (Concealed & Melded), Dora, and Ura-Dora.
- **Accurate Yaku Calculation**: Accurately handles complex hands such as Chiitoitsu (Seven Pairs) and Sananko (Three Concealed Triplets).
- **Japanese Yaku Names**: Clear display of scored yaku in traditional Japanese terminology.
- **Smart AI**: CPU opponent calculates shanten (distance to ready hand) for strategic discards.

## 1v1 Mahjong Rules

Designed for fast-paced gameplay with the following adjustments:

1. **Tiles Used (108 tiles total)**:
   - **Characters (Manzu)**: 1 and 9 only (2–8 excluded)
   - **Circles (Pinzu)**: 1 through 9
   - **Bamboo (Souzu)**: 1 through 9
   - **Honors (Zai)**: East, South, West, North, White, Green, Red
2. **Winning Conditions**:
   - Standard 4 melds + 1 pair, or **Chiitoitsu** (7 distinct pairs).
   - Must have at least 1 Yaku (Riichi and Tsumo count as Yaku).
3. **Melding**:
   - **Pon and Kan** are allowed (Chii is not allowed).
4. **Riichi**:
   - Declare when ready by paying 1,000 points. Auto-discards drawn tiles thereafter.
5. **Dora**:
   - The tile following the indicator is Dora. Winning after Riichi reveals **Ura-Dora**.
   - Kan reveals an additional New Dora indicator.

## How to Run

Requirements: Python 3.x and `uv`. Tile assets will be downloaded automatically on the first launch.

```bash
uv run main.py
```

## Controls

- **Discard Tile**: Click on any highlighted tile in your hand during your turn.
- **Action Buttons**: Buttons for RON, TSUMO, RIICHI, PON, KAN appear on the right when available.
- **Sound Effect**: Toggle via the SOUND button in the score panel or press **M**.
- **Restart Game**: Press **Spacebar** at the end of a match to proceed to the next round.

## License

- Source Code: MIT License
- Tile Images: [FluffyStuff/riichi-mahjong-tiles](https://github.com/FluffyStuff/riichi-mahjong-tiles) (CC0)
