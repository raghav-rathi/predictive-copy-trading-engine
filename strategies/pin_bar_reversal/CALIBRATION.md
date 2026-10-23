# Pin Bar Reversal — Calibration

All parameters were fixed a priori from the textbook pattern; no
optimization was performed on the backtest window and no parameter
sweep was run.

| Parameter | Value | Rationale |
|---|---|---|
| Tail fraction | 2/3 of range | Canonical pin shape: the rejection tail must dominate the bar |
| Body fraction | ≤ 1/3 of range | Real body must be small — indecision resolved against the tail |
| Opposite-wick fraction | ≤ 0.2 of range | Close near the extreme: the rejection won |
| Swing location | 5 bars | Pring location filter: rejection only counts at a local extreme |
| Stop | 1.0 × ATR | Just beyond the tail (tails run ~0.5–1.0 ATR on 1h crypto) |
| Target | 2.0 × ATR | Textbook 2R minimum risk/reward |
| Max hold | 48 bars (~2 days) | Reversal swings; stalled pins are dead pins |
| Risk per trade | 1% equity, 3× cap | Standard desk sizing |

**Geometric note:** when the tail and opposite-wick conditions both
hold, the body is automatically ≤ ~0.13 of the range (min(o,c) ≥
l + 2r/3 and max(o,c) ≤ h forces body ≤ r − 0.867r), so the
1/3-body rule is redundant — it never filters independently. Kept
for legibility, not for signal value.

**No sweep policy:** the shipped config was the first and only
config. Any future tuning must happen on walk-forward data, never
on the window in BACKTEST.md.
