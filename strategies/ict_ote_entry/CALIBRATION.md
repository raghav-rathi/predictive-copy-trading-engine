# ICT Optimal Trade Entry (OTE) — Calibration

Displacement-threshold sensitivity on the same Hyperliquid
1h data as BACKTEST.md (BTC/ETH/HYPE, pinned batch-47 window
2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC, 6,160 bars
BTC/ETH, 6,158 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 120-bar max hold). The displacement multiplier is the
strategy's natural knob: 1.0x ATR is a weaker displacement
requirement, 1.5x the shipped ICT-flavoured setting, 2.0x a
stricter one. The sweep re-runs `add_indicators(df,
disp_mult=X)` -- everything else (swing 20, OTE zone 62-79%,
24-bar expiry) stays fixed.

| Displacement | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 1.0x | BTC | 1 | 0.0% | -$114 | -1.45 | 0.00 | -$113.88 |
| 1.0x | ETH | 2 | 50.0% | +$113 | +0.56 | 3.58 | +$56.50 |
| 1.0x | HYPE | 6 | 50.0% | +$302 | +0.95 | 2.15 | +$50.40 |
| 1.5x (shipped) | BTC | 1 | 0.0% | -$114 | -1.45 | 0.00 | -$113.88 |
| 1.5x (shipped) | ETH | 2 | 50.0% | +$113 | +0.56 | 3.58 | +$56.50 |
| 1.5x (shipped) | HYPE | 5 | 60.0% | +$367 | +1.21 | 2.86 | +$73.37 |
| 2.0x | BTC | 1 | 0.0% | -$114 | -1.45 | 0.00 | -$113.88 |
| 2.0x | ETH | 1 | 100.0% | +$157 | +0.82 | inf | +$156.79 |
| 2.0x | HYPE | 5 | 60.0% | +$367 | +1.21 | 2.86 | +$73.37 |

## One-line verdict

- **1.0x:** combined +$302 on 9 trades -- one extra HYPE
  trade vs shipped, and it loses enough to pull HYPE from
  +$367 to +$302; the weaker threshold adds a loser.
- **1.5x:** the shipped setting -- combined +$366 on 8
  trades, the middle read.
- **2.0x:** combined +$410 on 7 trades -- the best combined
  read, entirely because one losing ETH trade drops out
  (ETH 2 trades -> 1, +$113 -> +$157).
- **Shipped decision:** keep the specified displacement
  multiplier = 1.5 as the registry config regardless. It was
  fixed before any backtest was run; the sweep is diagnostic
  only. The 2.0x "improvement" is one trade dropping out of
  a 7-trade sample, and BTC is identical (-$114, 1 trade)
  across all three settings -- the knob moves almost nothing
  because the sweep -> displacement -> retracement chain
  barely fires at any threshold. Do not ship a different
  threshold on the strength of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. Swing extremes
  are prior-bar rolling extremes (shifted by 1); ATR(14) is
  Wilder smoothing; the state machine only reads bars up to
  the current one; the near swing is frozen at the
  back-inside bar (a stored past value, not a future one);
  no `ichimoku` chikou column is used anywhere. The
  truncation test (`test_no_lookahead_truncation`) confirms
  indicator and signal values at bar j are identical whether
  computed on the full frame or on the frame truncated at j.
- **Source check:** the OTE construction (liquidity sweep,
  displacement / market-structure shift, 62-79% retracement
  entry, 70.5% optimal level) matches the cited ICT OTE
  references. Two documented deviations: (1) the house
  2xATR stop replaces ICT's structural stop beyond the leg
  start; (2) the zone is fixed at the displacement-
  confirmation bar and not redrawn if price extends further.
- **Tests:** 17/17 pass (`python3 -m unittest
  strategies.ict_ote_entry.test_ict_ote_entry`).
- **No parameter was tuned to PnL.** Displacement stays 1.5x.
