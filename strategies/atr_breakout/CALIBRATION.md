# ATR Expansion Breakout — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| ATR length | 14 | The spec's ATR length; the standard ATR setting. |
| ATR moving-average length | 20 | The spec's regime-filter length. |
| Range length | 20 bars | The spec's range length. |
| Range tightness | width <= 2.0 x ATR | The spec's tight-range gate. |
| Breakout buffer | 0.25 x ATR beyond the range level | The spec's buffer; filters marginal touches. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | Range needs 21 bars (20 + shift), ATR_MA20 needs ~34 bars to seed; 60 gives margin. |

## Spec decisions / ambiguities

1. **The range is the previous 20 bars' closes, shifted by 1.**
   The spec says "rolling 20-bar max of close SHIFTED by 1" —
   shipped literally. Without the shift a close could never break
   a max that includes itself.
2. **Range levels use closes, not highs/lows.** The spec defines
   the range from closes ("rolling 20-bar max of close"), shipped
   literally; a high/low range would be wider and break less often.
3. **Exit "back inside the range" is a close vs the same level.**
   Long exit is close < range_high (the previous-20 max close);
   short exit is close > range_low. The level is the same shifted
   series as the entry, so the exit can fire on the bar after a
   failed break.
4. **Expansion comparisons are strict.** ATR exactly equal to its
   20-bar average is neither expanding nor faded; entries need
   ATR > ATR_MA20, exits need ATR < ATR_MA20.
5. **Harness stop/trail as an additional exit.** The spec's exits
   are the back-inside / regime-faded exits; the batch-standard
   risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold) is
   applied on top, per the batch instruction.

## What the exits actually did

Shipped run (155 trades): 128 trades ended on a signal exit and 27
on the harness stop/trail (BTC 42 signal / 12 stop, ETH 48 / 12, HYPE
38 / 3). The back-inside / regime-faded signal exit dominates: the
ATR expansion that triggered the entry usually fades, or price falls
back inside the range, within a few bars — the breakout rarely holds
long enough for the stop or the trail to matter.

No bug fixes requiring re-runs, no PnL-selected tuning.
