# The Strat — Calibration

FTFC-gate sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, pinned batch-47 window
2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC, 6,160 bars
BTC/ETH, 6,158 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 120-bar max hold). The FTFC gate is the strategy's
natural knob: the shipped setting requires daily AND weekly
agreement, the alternates relax it to daily-only or drop it
entirely. The sweep re-runs the same setup logic with the
gate changed — the setups, exits, and risk are identical
throughout.

| FTFC gate | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| daily+weekly (shipped) | BTC | 420 | 25.2% | -$5,592 | -6.47 | 0.43 | -$13.32 |
| daily+weekly (shipped) | ETH | 402 | 26.9% | -$2,605 | -2.01 | 0.71 | -$6.48 |
| daily+weekly (shipped) | HYPE | 339 | 33.9% | -$3,175 | -3.64 | 0.57 | -$9.37 |
| daily-only | BTC | 804 | 25.0% | -$7,619 | -7.94 | 0.45 | -$9.48 |
| daily-only | ETH | 830 | 27.0% | -$5,269 | -3.57 | 0.67 | -$6.35 |
| daily-only | HYPE | 755 | 32.3% | -$5,671 | -5.41 | 0.57 | -$7.51 |
| none | BTC | 1,614 | 25.7% | -$9,482 | -12.34 | 0.46 | -$5.87 |
| none | ETH | 1,639 | 27.5% | -$8,272 | -6.70 | 0.64 | -$5.05 |
| none | HYPE | 1,485 | 34.3% | -$7,279 | -5.65 | 0.64 | -$4.90 |

## One-line verdict

- **daily+weekly:** combined -$11,372 on 1,161 trades —
  the shipped setting, the least-bad read in the sweep.
- **daily-only:** combined -$18,559 on 2,389 trades —
  relaxing the weekly leg roughly doubles the trade count
  and adds ~$7,200 of losses; the weekly filter is doing
  real work, just not enough.
- **none:** combined -$25,033 on 4,738 trades — the
  ungated setups fire ~4x as often and lose more than
  twice as much; per-trade expectancy is actually the
  best of the three (-$4.90 to -$5.87) because the gate
  keeps the larger losers, but the volume of trades
  overwhelms it.
- **Shipped decision:** keep the specified FTFC gate =
  daily AND weekly as the registry config regardless. It
  was fixed before any backtest was run; the sweep is
  diagnostic only. The gate being the least-bad of three
  losing settings is in-sample information, and every
  variant loses on every coin — the knob trims losses, it
  does not create an edge. Do not ship a different gate
  on the strength of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. Bar classes
  compare bar i only with bar i-1; FTFC directions come
  from completed blocks only (the block index is shifted
  by one, so a block's direction is applied only to bars
  after it closes); setups read the trigger bar and the
  two bars before it; no `ichimoku` chikou column is used
  anywhere. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the bar classification (1 inside, 2
  single-side break, 3 outside), the 2-1-2 / 3-1-2 / 2-2
  setup list, and the FTFC concept are per the task brief
  (LuxAlgo concept library / SmoothStrat course). One
  documented deviation: the book's trigger-break entry is
  replaced by a close-based signal on the trigger bar with
  next-bar-open execution, because the trigger is only
  known at the close on 1h bars.
- **Tests:** 16/16 pass (`python3 -m unittest
  strategies.the_strat.test_the_strat`).
- **No parameter was tuned to PnL.** FTFC gate stays
  daily+weekly.
