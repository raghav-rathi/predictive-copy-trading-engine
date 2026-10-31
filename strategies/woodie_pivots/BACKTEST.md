# Woodie Pivots — Backtest

**Data:** Hyperliquid 1h candles read directly from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) — `fetch_candles` was NOT called,
so the cache was not rewritten. Window t in [1773525600000,
1793318400000] (2026-03-14 22:00 UTC → 2026-10-30 00:00 UTC), duplicates
dropped (keep first). $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off. WARMUP = 50 bars.

**Bar counts used:** BTC 5499, ETH 5499, HYPE 5497. Before dedup the
window held 5504 / 5504 / 5502 rows, i.e. 5 exact-duplicate bars per
coin were dropped. First bar BTC/ETH 1773525600000 (2026-03-14
22:00 UTC), HYPE 1773532800000 (2026-03-15 00:00 UTC); last bar all
coins 1793318400000 (2026-10-30 00:00 UTC).

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 134 | 29.1% | -$1,273.90 | -0.97 | -18.7% | -$9.51 | 0.79 |
| ETH | 127 | 34.6% | -$447.05 | -0.22 | -16.1% | -$3.52 | 0.92 |
| HYPE | 136 | 33.8% | +$794.00 | +0.70 | -11.1% | +$5.84 | 1.12 |
| **Combined** | **397** | **32.5%** | **-$926.95** | **-0.24** | **-12.9%** | **-$2.33** | **0.95** |

Fees: BTC $1,509.36, ETH $1,127.76, HYPE $708.31 (total $3,345.43).
Exits: 342 stop / 55 signal / 0 max-hold — the stop manages 86% of
trades, meaning most R1/S1 breakouts reverse back through the
pivot and beyond the stop rather than running. Combined Sharpe /
MaxDD are computed on the summed $30k three-coin equity curve.

## Verdict: loser

-$927 across 397 trades, profit factor 0.95, green only on HYPE.
The breakout premise fails on this window: daily levels are
crossed, then price comes back — the PP exit triggers on only
14% of trades because the 2xATR stop usually fires first. A
breakout system whose exits are 86% stops is fading itself, not
riding breakouts.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Static all-day levels cannot adapt to intraday regime shifts.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
