# Floor-Trader Pivots

Classic floor-trader pivot breakout. Each bar, PP/R1/S1/R2/S2 are recomputed from the trailing 24 completed 1h bars (one "session"): H = max high, L = min low, C = close of the last completed bar; PP = (H+L+C)/3, R1 = 2*PP − L, S1 = 2*PP − H, R2 = PP + (H−L), S2 = PP − (H−L).

## Rules

- Bias: close above PP = long-only, close below PP = short-only.
- Long: close above R1 with volume above its 20-bar average → enter. Exit at R2 (close ≥ R2) or on a close back below PP.
- Short: close below S1 with volume above its 20-bar average → enter. Exit at S2 (close ≤ S2) or on a close back above PP.
- Levels use only the trailing 24 completed bars, so signals on bar i use no future data. ATR stop / trail from the risk layer also applies.

## Source

- EBC — How to Trade Using Classic Pivot Points: https://www.ebc.com/forex/how-to-trade-using-classic-pivot-points

Paper only, no live execution.
