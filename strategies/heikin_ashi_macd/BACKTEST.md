# Heikin Ashi + MACD Momentum Filter — Backtest

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
| BTC | 382 | 32.5% | -2789.77 | -1.63 | -41.1% | -7.30 | 0.81 |
| ETH | 384 | 32.0% | -2302.52 | -1.19 | -38.5% | -6.00 | 0.85 |
| HYPE | 402 | 34.8% | 2590.90 | 1.30 | -16.9% | 6.45 | 1.14 |
| **Combined** | **1168** | **33.1%** | **-2501.38** | **-0.51** | **-22.5%** | **-2.14** | **0.95** |

Fees: total $8758.18.
Exits: BTC {'stop': 237, 'signal': 145}; ETH {'stop': 267, 'signal': 117}; HYPE {'stop': 250, 'signal': 152}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$27416.94.

## Verdict: LOSER — -$2,501.38 on 1168 trades, combined Sharpe -0.51, MaxDD -22.5%.

The filter loses on two of three coins and barely breaks even
combined (PF 0.95). BTC and ETH both lose over $2,300 with win
rates around 32% and MaxDDs near -40%; only HYPE wins (+$2,590.90,
PF 1.14, Sharpe 1.30). The system trades far too often for a
momentum filter — 1168 trades in ~8 months, roughly 4–5 per coin
per day — and $8,758.18 of fees eats the gross edge: the histogram
zero-cross whipsaws in choppy 1h crypto, so entries fire mid-chop
and the 2xATR stop takes most of them (754 of 1168 exits are
stops). The signal exit does real work here (414 of 1168 exits),
so the loss is in the entry timing, not a missing exit. No
parameter was tuned; the spec is shipped as written.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 1168-trade sample, but the result is HYPE-only in the green —
  the edge is not universal across coins.
- The HA-direction filter blocks entries at sharp V-reversals
  (the pivot bar's HA candle still points the old way), so the
  system systematically misses the cleanest turns and enters
  mid-move instead.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
