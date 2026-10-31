# Wilder Accumulative Swing Index — Backtest

**Data:** Hyperliquid 1h candles read directly from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) — `fetch_candles` was NOT called,
so the cache was not rewritten. Window t in [1773525600000,
1793318400000] (2026-03-14 22:00 UTC → 2026-10-30 00:00 UTC), duplicates
dropped (keep first). $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off. WARMUP = 20 bars.

**Bar counts used:** BTC 5499, ETH 5499, HYPE 5497. Window rows before
dedup: 5504 / 5504 / 5502, i.e. 5 exact-duplicate bars dropped per
coin. First bar BTC/ETH 1773525600000 (2026-03-14 22:00 UTC), HYPE
1773532800000 (2026-03-15 00:00 UTC); last bar all coins
1793318400000 (2026-10-30 00:00 UTC).

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 1,158 | 21.1% | −$8,701.76 | −9.81 | −87.2% | −$7.51 | 0.49 |
| ETH | 1,092 | 23.3% | −$6,521.93 | −4.84 | −67.9% | −$5.97 | 0.68 |
| HYPE | 1,049 | 24.8% | −$6,039.80 | −4.64 | −65.3% | −$5.76 | 0.71 |
| **Combined** | **3,299** | **23.0%** | **−$21,263.49** | **−8.94** | **−72.7%** | **−$6.45** | **0.63** |

Fees: BTC $5,521.61, ETH $5,755.07, HYPE $3,347.50 (total $14,624.17).
Exits: 2,479 signal / 820 stop / 0 max-hold. Combined Sharpe / MaxDD
are computed on the summed $30k three-coin equity curve truncated to
the shortest series (5497 bars); combined totals are sums of the
per-coin runs.

## Verdict: worst loser of the batch — do not trade

−$21,263 on $30k starting capital (−71%), a combined Sharpe of −8.94,
and a −72.7% max drawdown across 3,299 trades is a comprehensive
rejection. The ASI-vs-EMA crossover fires constantly in chop (over
1,000 trades per coin) with a ~23% win rate, and the BTC equity curve
loses 87% peak-to-trough. Nothing in this configuration survives
contact with the window; the ASI may have uses as a trend-confirmation
overlay, but as a standalone crossover trigger it is decisively
negative here.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- The implemented R variant is documented in README.md; a different
  Wilder R variant would give different numbers and was not tested.
- Never tune the shipped parameters on this window.
