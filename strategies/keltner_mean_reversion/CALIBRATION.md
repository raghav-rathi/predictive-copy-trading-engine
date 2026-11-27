# Keltner Mean Reversion — Calibration

Band-multiplier sensitivity on the same Hyperliquid 1h data
as BACKTEST.md (BTC/ETH/HYPE, pinned batch-48 window
2026-03-14 22:00 UTC → 2026-11-27 14:00 UTC, 6,184 bars
BTC/ETH, 6,182 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 72-bar max hold). The multiplier k is the strategy's
natural knob: 1.5x is a narrower band (more tags), 2.0x the
shipped setting, 2.5x wider (fewer tags). The sweep re-runs
`add_indicators(df, k=X)` -- everything else (EMA 20, ATR
10, entry/exit rules) stays fixed.

| Band k | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 1.5 | BTC | 0 | — | $0 | 0.00 | 0.00 | $0.00 |
| 1.5 | ETH | 0 | — | $0 | 0.00 | 0.00 | $0.00 |
| 1.5 | HYPE | 0 | — | $0 | 0.00 | 0.00 | $0.00 |
| 2.0 (shipped) | BTC | 0 | — | $0 | 0.00 | 0.00 | $0.00 |
| 2.0 (shipped) | ETH | 0 | — | $0 | 0.00 | 0.00 | $0.00 |
| 2.0 (shipped) | HYPE | 0 | — | $0 | 0.00 | 0.00 | $0.00 |
| 2.5 | BTC | 0 | — | $0 | 0.00 | 0.00 | $0.00 |
| 2.5 | ETH | 0 | — | $0 | 0.00 | 0.00 | $0.00 |
| 2.5 | HYPE | 0 | — | $0 | 0.00 | 0.00 | $0.00 |

## One-line verdict

- **1.5x / 2.0x / 2.5x:** combined 0 trades at every
  setting. The multiplier is not the binding constraint --
  the candle-direction filter is (see BACKTEST.md): a
  band-cross bar is directional by construction on chained
  1h opens, so no k makes the filter coincide with a cross.
- **Shipped decision:** keep the specified band multiplier
  = 2.0 as the registry config regardless. It was fixed
  before any backtest was run; the sweep is diagnostic
  only.

## Diagnostic: without the candle filter (NOT shipped)

To check whether the filter is hiding a winner, the same
k=2.0 run was repeated with the candle-direction condition
removed (cross-only entries, same exits/risk). This variant
is diagnostic only and is not the shipped strategy.

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| k=2.0, no filter | BTC | 192 | 46.4% | -$2,122 | -1.83 | 0.75 | -$11.05 |
| k=2.0, no filter | ETH | 188 | 46.3% | -$2,291 | -1.78 | 0.76 | -$12.18 |
| k=2.0, no filter | HYPE | 212 | 50.9% | -$883 | -0.70 | 0.90 | -$4.16 |

Combined: 592 trades, -$5,296, fees $4,102.35. Exits:
BTC stop 106 / signal 86; ETH stop 101 / signal 87; HYPE
stop 106 / signal 106. The unfiltered fade also loses on
every coin (stops dominate the exits), so dropping the
filter would not rescue the strategy -- it would only turn
a silent zero into a loud loser. The filter stays as
specified.

## Audit

- **Lookahead audit:** no lookahead found. EMA and Wilder
  ATR are causal recursions; the entry cross and the
  candle direction are judged on the same closed bar; the
  exit cross is judged on the closed bar. The truncation
  test (`test_no_lookahead_truncation`) confirms indicator
  and signal values at bar j are identical whether
  computed on the full frame or on the frame truncated at
  j.
- **Source check:** the construction (Keltner EMA(20) /
  ATR(10) / k=2.0, cross-plus-reversal-candle entry, exit
  on a cross back to the midline) matches the cited
  Keltner reference. No deviation from the source: the
  zero-trade result is the specified rule's honest output
  on 1h crypto, and no rule was relaxed to make it fire.
- **Tests:** 12/12 pass (`python3 -m unittest
  strategies.keltner_mean_reversion.test_keltner_mean_reversion`).
- **No parameter was tuned to PnL.** Band multiplier stays 2.0.
