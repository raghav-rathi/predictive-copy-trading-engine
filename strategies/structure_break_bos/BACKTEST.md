# Structure Break (BOS) — Backtest

**Data:** Hyperliquid 1h candles read directly from the
local cache (`data/candles/{BTC,ETH,HYPE}_1h.csv`; no
`fetch_candles` call, cache untouched), window t in
[1773525600000, 1793318400000] (2026-03-14 22:00 UTC →
2026-10-30 00:00 UTC), duplicate t dropped (keep first).
Bar counts match the expected counts exactly: BTC 5499,
ETH 5499, HYPE 5497 (HYPE's first bar is 2026-03-15 00:00
UTC; the cache also contained 5 exact-duplicate bars per
coin, dropped before running). $10k start per coin, 1% risk
per trade on the 2xATR stop, 3x leverage cap, 0.045% fee +
0.01% slippage per side, funding off, warmup 20 bars, run
through `strategies/backtest.py` `run_backtest`.

## Results (shipped config: 5-bar pivots confirmed after
2 bars, BOS-continuation entry, opposite-break exit,
2xATR stop, 2.5xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 149 | 31.5% | -$1,409.00 | -1.05 | -18.1% | -$9.46 | 0.80 |
| ETH | 145 | 29.7% | -$510.99 | -0.31 | -16.0% | -$3.52 | 0.93 |
| HYPE | 139 | 37.4% | +$2,203.19 | +1.63 | -9.9% | +$15.85 | 1.33 |
| **Combined** | **433** | **32.8%** | **+$283.20** | +0.18 | -8.0% | **+$0.65** | — |

Fees: BTC $1,589.69, ETH $1,255.98, HYPE $822.12 (total
$3,667.78). Exits: 351 stop / 82 signal / 0 max-hold.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (truncated to the 5,497-bar common
length; the summed net PnL above is exact).

## Verdict: no demonstrated edge (flat, not a win)

+$283 across 433 trades is 0.9% over ~7.5 months — noise.
HYPE carries the book (+$2,203) while BTC (-$1,409) and ETH
(-$511) both lose, and the win rate is only 32.8%. A
continuation rule that loses on the two most liquid coins
is not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- HYPE history starts 2 hours later than BTC/ETH in this window.
- Never tune the shipped parameters on this window.
