# Asian Range Breakout — Backtest

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
0.01% slippage per side, funding off, warmup 25 bars, run
through `strategies/backtest.py` `run_backtest`.

## Results (shipped config: UTC [0, 8) Asian range, first
post-08:00 breakout with volume above its 20-bar average,
16:00 UTC time exit, 2xATR stop, 2.5xATR trail, 24-bar max
hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 171 | 35.7% | -$1,519.74 | -1.47 | -20.8% | -$8.89 | 0.76 |
| ETH | 153 | 42.5% | +$1,487.84 | +1.36 | -9.6% | +$9.72 | 1.31 |
| HYPE | 176 | 46.0% | -$1,153.90 | -1.43 | -17.5% | -$6.56 | 0.77 |
| **Combined** | **500** | **41.4%** | **-$1,185.80** | -0.50 | -14.3% | **-$2.37** | — |

Fees: BTC $1,794.17, ETH $1,346.15, HYPE $812.47 (total
$3,952.79). Exits: 326 signal (time exits) / 174 stop /
0 max-hold. Combined Sharpe / MaxDD are computed on the
summed $30k three-coin equity curve (truncated to the
5,497-bar common length; the summed net PnL above is
exact).

## Verdict: loser (ETH green does not save it)

-$1,186 across 500 trades. ETH's +$1,488 does not offset
BTC (-$1,520) and HYPE (-$1,154), and a single-coin win with
two coins losing at similar trade counts is not a robust
edge — it is coin selection after the fact.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry (the 16:00
  time exit therefore executes at the 17:00 open).
- HYPE history starts 2 hours later than BTC/ETH in this window.
- Never tune the shipped parameters on this window.
