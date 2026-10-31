# Chande Momentum Oscillator — Backtest

**Data:** Hyperliquid 1h candles read directly from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) — `fetch_candles` was NOT called,
so the cache was not rewritten. Window t in [1773525600000,
1793318400000] (2026-03-14 22:00 UTC → 2026-10-30 00:00 UTC), duplicates
dropped (keep first). $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off. WARMUP = 20 bars.

**Bar counts used:** BTC 5499, ETH 5499, HYPE 5497. Before dedup the
window held 5504 / 5504 / 5502 rows, i.e. 5 exact-duplicate bars per
coin were dropped. First bar BTC/ETH 1773525600000 (2026-03-14 22:00
UTC), HYPE 1773532800000 (2026-03-15 00:00 UTC); last bar all coins
1793318400000 (2026-10-30 00:00 UTC).

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 141 | 40.4% | -$1,673.83 | -1.66 | -19.6% | -$11.87 | 0.71 |
| ETH | 144 | 38.9% | -$707.87 | -0.64 | -15.1% | -$4.92 | 0.87 |
| HYPE | 128 | 37.5% | -$2,037.74 | -2.57 | -21.8% | -$15.92 | 0.63 |
| **Combined** | **413** | **39.0%** | **-$4,419.44** | **-2.43** | **-18.4%** | **-$10.70** | **0.74** |

Fees: BTC $1,475.64, ETH $1,143.86, HYPE $583.03 (total $3,202.54).
Exits: 237 stop / 176 signal / 0 max-hold. Combined Sharpe / MaxDD
are computed on the summed $30k three-coin equity curve.

## Verdict: loser on all three coins, not a demonstrated edge

-$4,419 across 413 trades on $30k starting capital over ~7.5 months,
losing on BTC, ETH, and HYPE alike with the worst combined Sharpe of
this batch (-2.43). The highest win rate of the three strategies
(39.0%) does not save it: winners are too small relative to losers
(profit factor 0.74). Leaving an extreme zone is a poor entry trigger
on this window.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- CMO threshold crossings are frequent in chop, generating 413 trades
  and $3,203 of fees.
- Never tune the shipped parameters on this window.
