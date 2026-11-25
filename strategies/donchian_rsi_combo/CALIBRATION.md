# Donchian RSI Combo — Calibration

Entry-window sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, pinned batch-46 window
2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC, 6,136 bars
BTC/ETH, 6,134 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 120-bar max hold). The entry channel window is the
strategy's natural knob: 10 bars is the faster Turtle
system, 20 the standard, 55 the slower Turtle system. The
sweep re-runs `add_indicators(df, entry_n=X)` and
`add_signals(df, entry_n=X)` — the exit channel stays 10
bars and the RSI filter stays 70/30 throughout. (The sweep
itself caught a bug: `add_signals` originally hardcoded the
20-bar columns, so entry_n != 20 raised a KeyError. Signals
now take `entry_n`/`exit_n` parameters; the shipped 20-bar
backtest was re-run after the fix and is unchanged.)

| Entry window | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10 | BTC | 276 | 31.5% | -$2,499 | -1.20 | 0.81 | -$9.05 |
| 10 | ETH | 267 | 36.0% | +$23 | +0.21 | 1.00 | +$0.09 |
| 10 | HYPE | 281 | 34.5% | +$1,023 | +0.76 | 1.06 | +$3.64 |
| 20 (shipped) | BTC | 177 | 30.5% | -$1,935 | -1.11 | 0.76 | -$10.93 |
| 20 (shipped) | ETH | 159 | 37.1% | +$1,411 | +1.03 | 1.19 | +$8.87 |
| 20 (shipped) | HYPE | 200 | 35.0% | +$1,166 | +0.87 | 1.10 | +$5.83 |
| 55 | BTC | 60 | 31.7% | -$1,347 | -1.60 | 0.53 | -$22.44 |
| 55 | ETH | 49 | 34.7% | -$1,012 | -1.16 | 0.61 | -$20.66 |
| 55 | HYPE | 82 | 28.0% | -$1,343 | -1.36 | 0.70 | -$16.38 |

## One-line verdict

- **10:** combined -$1,453 on 824 trades — the fastest
  channel trades the most and pays the most fees ($5,349);
  HYPE stays positive (+$1,023) but ETH collapses to +$23
  and BTC worsens to -$2,499.
- **20:** the shipped setting — the only positive combined
  read (+$642, 536 trades); the best ETH (+$1,411) and
  HYPE (+$1,166) reads in the sweep sit here, and BTC is
  still negative (-$1,935).
- **55:** combined -$3,702 on 191 trades — negative on
  every coin, the worst combined read by far; the slow
  Turtle channel catches breakouts too late on 1h bars
  (expectancy -$16 to -$22 per trade).
- **Shipped decision:** keep the specified entry window =
  20 as the registry config regardless. It was fixed before
  any backtest was run; the sweep is diagnostic only. The
  20-bar window being the only positive combined read is
  in-sample information, and the 10- and 55-bar reads
  bracket it with losses on both sides — the knob is not
  stable, it is just the middle of three losing-or-marginal
  settings. Do not ship a different window on the strength
  of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. Donchian
  channels are causal rolling extremes; RSI(14) is Wilder
  smoothing; signals compare the close against the
  channels shifted by 1 (prior bars only); no `ichimoku`
  chikou column is used anywhere. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the channel construction (highest high
  / lowest low of the last N periods, N usually 20) and the
  long-above / short-below rule are confirmed by the cited
  Wikipedia page (verified via web search 2026-11-25).
  One documented deviation: the 10-bar Turtle exit is
  judged against the prior bars' channel (shifted by 1),
  because the unshifted 10-bar low includes the current
  bar's own low and the close can never be below it — the
  unshifted reading could never fire.
- **Tests:** 15/15 pass (`python3 -m unittest
  strategies.donchian_rsi_combo.test_donchian_rsi_combo`).
- **No parameter was tuned to PnL.** Entry window stays 20.
