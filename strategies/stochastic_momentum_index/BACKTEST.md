# Stochastic Momentum Index — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794488400000) (2026-03-14 22:00 UTC →
2026-11-12 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5823, ETH 5823, HYPE 5821.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 85 | 36.5% | -784.88 | -0.76 | -14.2% | -9.23 | 0.81 |
| ETH | 79 | 40.5% | 1189.40 | 1.15 | -8.9% | 15.06 | 1.33 |
| HYPE | 111 | 39.6% | 1282.61 | 1.14 | -7.9% | 11.56 | 1.24 |
| **Combined** | **275** | **38.9%** | **1687.13** | **0.78** | **-6.7%** | **6.14** | **1.13** |

Fees: total $2074.79.
Exits: BTC {'stop': 76, 'signal': 9}; ETH {'stop': 71, 'signal': 8}; HYPE {'stop': 104, 'signal': 7}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$31,687.13.

## Verdict: WINNER — +$1,687.13 on 275 trades, combined Sharpe 0.78, MaxDD -6.7%.

Blau's SMI is the second genuine winner in the batch series: ETH
+$1,189.40 (Sharpe 1.15, PF 1.33) and HYPE +$1,282.61 (Sharpe 1.14,
PF 1.24) carry the book, and only BTC loses (-$784.88, PF 0.81).
Win rate 38.9% with PF 1.13 clears $2,074.79 in fees and banks
+$1,687.13 net. The honest caveat is in the exit split: 251 of 275
trades ended on the harness stop/trail and only 24 on the zero-line
cross, so the shipped system is effectively an SMI +/-40-zone entry
plus the 2xATR stop / 2.5xATR trail — the zero-line exit is decorative
in practice, and the edge lives in the entry selectivity (the slow
EMA(25,2) double smoothing means the SMI only crosses -40/+40 on
sustained momentum shifts, not on every wiggle). MaxDD -6.7% on the
combined curve is the mildest in this batch.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 275-trade sample: a real sample, but one window and two of three
  coins driving the result — BTC's loss is a reminder the edge is
  not universal across coins.
- The zero-line exit almost never fires (24/275); the reported
  result is really the entry + harness stop/trail, not Blau's full
  system as written.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
