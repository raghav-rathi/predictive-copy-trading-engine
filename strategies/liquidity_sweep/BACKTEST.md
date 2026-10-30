# Liquidity Sweep — Backtest

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

## Results (shipped config: prior-20-bar swing levels,
wick + reclaim on the sweep bar or the next bar,
opposite-sweep exit, 2xATR stop, 2.5xATR trail, 120-bar
max hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 171 | 36.3% | -$1,711.28 | -1.47 | -25.6% | -$10.01 | 0.80 |
| ETH | 166 | 37.3% | -$2,769.40 | -2.89 | -31.8% | -$16.68 | 0.65 |
| HYPE | 179 | 40.2% | -$280.16 | -0.15 | -18.1% | -$1.57 | 0.96 |
| **Combined** | **516** | **38.0%** | **-$4,760.83** | -2.36 | -22.5% | **-$9.23** | — |

Fees: BTC $1,840.94, ETH $1,400.21, HYPE $817.14 (total
$4,058.29). Exits: 358 stop / 158 signal / 0 max-hold.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (truncated to the 5,497-bar common
length; the summed net PnL above is exact).

## Verdict: loser

-$4,761 across 516 trades, negative on every coin, worst
on ETH (-$2,769, Sharpe -2.89, -31.8% max drawdown). The
reclaim does not predict continuation on this timeframe:
sweeps revert into the range and then keep going, or the
reclaim itself is the top/bottom of a chop sequence.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- HYPE history starts 2 hours later than BTC/ETH in this window.
- Never tune the shipped parameters on this window.
