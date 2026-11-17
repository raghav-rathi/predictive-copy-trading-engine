# Supertrend RSI — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794924000000) (2026-03-14 22:00 UTC →
2026-11-17 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5944, ETH 5944, HYPE 5942.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 168 | 31.0% | -1570.31 | -1.09 | -23.2% | -9.35 | 0.81 |
| ETH | 160 | 34.4% | -174.40 | -0.01 | -14.8% | -1.09 | 0.98 |
| HYPE | 160 | 33.8% | -686.63 | -0.38 | -17.4% | -4.29 | 0.92 |
| **Combined** | **488** | **33.0%** | **-2431.34** | **-0.76** | **-14.6%** | **-4.98** | **0.90** |

Fees: total $3670.21.
Exits: BTC {'stop': 154, 'signal': 14}; ETH {'stop': 147, 'signal': 13}; HYPE {'stop': 151, 'signal': 9}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$27,567.01.

## Verdict: LOSER — -$2,431.34 on 488 trades, combined Sharpe -0.76, MaxDD -14.6%.

Supertrend + RSI(14) loses on all three coins, though less badly
than the trendline system: BTC -$1,570.31 (PF 0.81), ETH
-$174.40 (PF 0.98 — essentially breakeven), HYPE -$686.63
(PF 0.92). Win rates 31–34% with expectancy -$1.09 to -$9.35
per trade; the combined PF of 0.90 does not clear $3,670.21 in
fees. The honest caveat is in the exit split: only 36 of 488
trades ended on the Supertrend flip and 452 on the harness
stop/trail — the flip is a slow exit, so the system is effectively
an RSI-50-cross entry plus the 2xATR stop / 2.5xATR trail, and the
entry's edge (RSI crossing 50 while price sits on the trend side)
is not enough to beat the stop on 1h crypto chop. ETH at
breakeven is the only near-miss; nothing here clears the bar.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 488-trade sample; the loss is broad-based across all three
  coins, so it is not a one-coin artifact.
- The Supertrend-flip exit almost never fires (36/488); the
  reported result is really the entry + harness stop/trail, not
  the full Supertrend-to-flip system as written.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
