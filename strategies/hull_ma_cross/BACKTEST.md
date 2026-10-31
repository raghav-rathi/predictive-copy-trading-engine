# Hull MA Cross — Backtest

**Data:** Hyperliquid 1h candles read directly from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) — `fetch_candles` was NOT called,
so the cache was not rewritten. Window t in [1773525600000,
1793318400000] (2026-03-14 22:00 UTC → 2026-10-30 00:00 UTC), duplicates
dropped (keep first). $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off. WARMUP = 80 bars.

**Bar counts used:** BTC 5499, ETH 5499, HYPE 5497. Before dedup the
window held 5504 / 5504 / 5502 rows, i.e. 5 exact-duplicate bars per
coin were dropped. First bar BTC/ETH 1773525600000 (2026-03-14
22:00 UTC), HYPE 1773532800000 (2026-03-15 00:00 UTC); last bar all
coins 1793318400000 (2026-10-30 00:00 UTC).

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 283 | 34.3% | -$2,090.55 | -1.26 | -26.5% | -$7.39 | 0.83 |
| ETH | 295 | 33.9% | -$1,469.35 | -0.75 | -28.3% | -$4.98 | 0.89 |
| HYPE | 300 | 37.0% | +$3,725.80 | +1.95 | -16.6% | +$12.42 | 1.23 |
| **Combined** | **878** | **35.1%** | **+$165.90** | **+0.19** | **-14.3%** | **+$0.19** | **1.00** |

Fees: BTC $3,117.87, ETH $2,476.47, HYPE $1,981.66 (total $7,576.00).
Exits: 655 stop / 223 signal / 0 max-hold — the stop manages 75% of
trades. Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: breakeven, not an edge

+$166 across 878 trades on $30k starting capital, with a profit
factor of exactly 1.00, is noise around breakeven. The HYPE leg
(+$3,726, Sharpe +1.95) is fully offset by BTC and ETH bleeding
(-$3,560 combined) — a single-coin win in a trending coin does not
make the cross a system. The 2xATR stop still manages three
quarters of all exits, which is the signature of a whipsaw-prone
cross, HMA's lag reduction notwithstanding. Loser on 2 of 3 coins;
not tradeable as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- HYPE's green leg may be trend-regime luck, not a structural edge.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
