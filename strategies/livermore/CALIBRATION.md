# Livermore — Calibration

Breakout-lookback sensitivity on the same Hyperliquid 1h data
as BACKTEST.md (BTC/ETH/HYPE, window ms
`[1773525600000, 1795525200000)`, 2026-03-14 22:00 UTC →
2026-11-24 14:00 UTC, same costs/sizing, 2xATR stop, 3xATR
trail, 60-bar max hold). Re-run on the batch-45 window; the
stale Nov-14 sweep numbers have been replaced. The lookback is
the strategy's natural knob: how far back the breakout level
reaches — 10 is a short, twitchy breakout (more setups), 30 a
longer, more significant one (fewer setups). The sweep re-runs
`add_indicators(df, breakout_lookback=X)` only — signals and
risk are unchanged.

| breakout | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10 | BTC | 181 | 33.70% | +$62.15 | +0.16 | 1.01 | +$0.34 |
| 10 | ETH | 187 | 34.76% | +$1,196.77 | +0.74 | 1.13 | +$6.40 |
| 10 | HYPE | 184 | 33.15% | -$1,049.53 | -0.60 | 0.89 | -$5.70 |
| 20 (shipped) | BTC | 139 | 33.09% | -$86.55 | +0.05 | 0.99 | -$0.62 |
| 20 (shipped) | ETH | 133 | 34.59% | +$800.88 | +0.60 | 1.12 | +$6.02 |
| 20 (shipped) | HYPE | 152 | 32.89% | -$1,477.93 | -1.05 | 0.81 | -$9.72 |
| 30 | BTC | 120 | 34.17% | -$249.99 | -0.09 | 0.96 | -$2.08 |
| 30 | ETH | 118 | 33.90% | +$24.49 | +0.12 | 1.00 | +$0.21 |
| 30 | HYPE | 136 | 33.09% | -$1,036.10 | -0.72 | 0.85 | -$7.62 |

Combined: 10 → 552 trades, +$209.38; 20 (shipped) → 424
trades, -$763.60; 30 → 374 trades, -$1,261.60.

## One-line verdict

- **10:** loosest breakout, most trades (552) — least-bad
  combined (+$209.38) and best on BTC (+$62.15, PF 1.01) and
  ETH (+$1,196.77, PF 1.13), but still losing on HYPE
  (-$1,049.53). Note the combined number is barely positive —
  +$209 on 552 trades is noise, not an edge.
- **30:** strictest breakout, fewest trades (374) — worst
  combined (-$1,261.60) and worst on BTC (-$249.99). Waiting
  longer for the breakout just means entering later into moves
  that still don't persist.
- **20:** middle ground (-$763.60 combined) — worst on HYPE
  (-$1,477.93) and best on no coin.
- **Shipped decision:** keep the specified
  breakout_lookback=20 as the registry config regardless.
  It was fixed before any backtest was run; adopting 10
  *because* it is least-bad in-sample would still be
  in-sample selection — and on this window 10's combined edge
  is +$0.38/trade, i.e. nothing. The honest read: the knob is
  nearly flat (combined net spans +$209 to -$1,262, all within
  noise of zero, PF 0.81–1.13 per coin) — the problem is not
  how far back the breakout level reaches, it is that a 1h
  breakout with a 10-bar higher-lows filter does not define a
  tradeable trend on this window.

## Batch-45 audit note

Refresh audit (Nov 24, 2026): no lookahead, no NaN poisoning,
no exit-logic bug found in indicators/signals/risk. All 15
tests pass. No code changed; parameters untouched. The only
file change in this refresh was filling in the empty
`source_url` in `__init__.py` (verified MQL5 article on
Livermore's Pivotal Point System:
https://www.mql5.com/en/articles/24075).
