# Fibonacci Time Zones Pullback — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795096800000) (2026-03-14 22:00 UTC →
2026-11-19 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5992, ETH 5992, HYPE 5990.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 42 | 33.3% | -159.75 | -0.19 | -7.7% | -3.80 | 0.93 |
| ETH | 49 | 28.6% | 150.74 | 0.23 | -10.1% | 3.08 | 1.06 |
| HYPE | 37 | 37.8% | 1357.56 | 1.46 | -5.9% | 36.69 | 1.90 |
| **Combined** | **128** | **32.8%** | **1348.55** | **0.86** | **-5.0%** | **10.54** | **1.21** |

Fees: total $1134.88.
Exits: BTC {'stop': 35, 'signal': 7}; ETH {'stop': 40, 'signal': 9}; HYPE {'stop': 35, 'signal': 2}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$31,348.55.

## Verdict: WINNER (nominal, thin sample) — +$1,348.55 on 128 trades, combined Sharpe 0.86, MaxDD −5.0%.

The combined row is green, but the profit is HYPE-carried:
HYPE is +$1,357.56 (PF 1.90, expectancy +$36.69/trade) while BTC
loses −$159.75 and ETH wins only +$150.74. With 128 trades the
combined +$1,348.55 is a real positive print, not a single-trade
artifact, yet one coin supplying the whole profit means the edge
claim is fragile — HYPE's 37 trades decide the verdict. Fees
($1,134.88) are large relative to the profit, and the win rate
(32.8%) with a 2xATR stop means the system lives on its winners
running. No parameter was tuned; the spec shipped as written.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 128 trades, and the combined win rests almost entirely on HYPE
  — not a robust edge claim; BTC loses and ETH is flat.
- The pullback may dip at the anchor itself (the swing low is
  usually already below EMA(20)); the zone only gates the
  reclaim bar, not the dip (see CALIBRATION.md).
- Never tune the shipped parameters on this window.

Paper only, no live execution.
