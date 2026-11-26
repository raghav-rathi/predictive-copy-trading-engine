# ICT Killzone — Calibration

Displacement-threshold sensitivity on the same Hyperliquid
1h data as BACKTEST.md (BTC/ETH/HYPE, pinned batch-47 window
2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC, 6,160 bars
BTC/ETH, 6,158 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 24-bar max hold). The displacement multiplier is the
strategy's natural knob: 0.75x ATR is a weaker displacement
requirement, 1.0x the shipped setting, 1.5x a stricter one.
The sweep re-runs `add_indicators(df, disp_mult=X)` --
everything else (Asian range, killzone windows, 50% entry,
day-boundary expiry) stays fixed.

| Displacement | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 0.75x | BTC | 1 | 100.0% | +$4 | +0.05 | inf | +$4.49 |
| 0.75x | ETH | 1 | 100.0% | +$5 | +0.13 | inf | +$5.35 |
| 0.75x | HYPE | 0 | — | $0 | 0.00 | 0.00 | $0.00 |
| 1.0x (shipped) | BTC | 1 | 100.0% | +$4 | +0.05 | inf | +$4.49 |
| 1.0x (shipped) | ETH | 1 | 100.0% | +$5 | +0.13 | inf | +$5.35 |
| 1.0x (shipped) | HYPE | 0 | — | $0 | 0.00 | 0.00 | $0.00 |
| 1.5x | BTC | 0 | — | $0 | 0.00 | 0.00 | $0.00 |
| 1.5x | ETH | 0 | — | $0 | 0.00 | 0.00 | $0.00 |
| 1.5x | HYPE | 0 | — | $0 | 0.00 | 0.00 | $0.00 |

## One-line verdict

- **0.75x:** combined +$10 on 2 trades -- identical to
  shipped; the weaker threshold arms more setups but none
  of the extra ones reach the 50% entry.
- **1.0x:** the shipped setting -- combined +$10 on 2 trades.
- **1.5x:** combined $0 on 0 trades -- the stricter
  displacement kills both entries; the strategy goes fully
  silent.
- **Shipped decision:** keep the specified displacement
  multiplier = 1.0 as the registry config regardless. It was
  fixed before any backtest was run; the sweep is diagnostic
  only. The knob barely matters here -- the binding
  constraint is the 50% retracement entry, not the
  displacement size -- and 0.75x vs 1.0x being identical on
  2 trades says the threshold is not what decides outcomes.
  Do not ship a different threshold on the strength of this
  sweep.

## Audit

- **Lookahead audit:** no lookahead found. The Asian range
  uses only the 00:00-03:00 UTC bars of the current day (and
  is NaN before 03:00); swing extremes are prior-bar rolling
  extremes (shifted by 1); ATR(14) is Wilder smoothing; the
  state machine only reads bars up to the current one; the
  near swing is frozen at the back-inside bar (a stored past
  value, not a future one); no `ichimoku` chikou column is
  used anywhere. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the killzone construction (Asian range,
  London 07:00-10:00 UTC / NY 12:00-14:00 UTC windows, sweep
  then displacement then retracement entry) matches the cited
  ICT killzone references. Two documented deviations: (1)
  windows include their end-hour bar and an armed setup's
  retracement entry may land after the window closes
  (expiring at the UTC day boundary) -- the strict reading is
  unfireable on 1h bars; (2) the 50% entry level
  approximates the FVG by the displacement leg's midpoint.
- **Tests:** 18/18 pass (`python3 -m unittest
  strategies.ict_killzone.test_ict_killzone`).
- **No parameter was tuned to PnL.** Displacement stays 1.0x.
