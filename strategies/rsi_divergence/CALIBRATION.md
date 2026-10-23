# RSI Divergence — Calibration note

**All parameters fixed a priori. No optimization was performed.**

- **RSI length 14** — Wilder's canonical length, and the length used
  in the TradingSim divergence ruleset the mechanism is taken from.
- **Pivot left=right=3** — the standard swing-pivot window used by
  TradingView's built-in pivot points and the community
  RSI-divergence scripts (3/3 is the modal choice; larger windows
  miss 1h swing structure, smaller windows drown in noise).
- **ATR(14), 1.5x stop, 2x trail** — the repo-wide divergence-family
  convention (same as obv_divergence's risk layer).
- **max_hold_bars=96** — ~4 days on 1h bars; a divergence reversal
  that has not resolved in 4 days is a failed premise.
- **WARMUP=80** — RSI(14) spin-up plus pivot-confirmation margin.

No parameter sweep was run on the backtest window. Any future tuning
must be done on walk-forward data, never on the window reported in
BACKTEST.md.
