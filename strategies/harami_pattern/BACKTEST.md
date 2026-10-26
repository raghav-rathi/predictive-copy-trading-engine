# harami_pattern — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`): BTC/ETH 5,384 bars,
2026-03-14 22:00 UTC → 2026-10-25 00:00 UTC; HYPE 5,382 bars,
2026-03-15 00:00 UTC → 2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop (VCP: 1.5xATR),
3x leverage cap, $10k start, long/short except VCP (long only).

## Results (shipped config: small body inside large body; large >1%, small <50%)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 23 | 34.8% | $-463 | -1.10 | -6.1% | $-20.14 | 0.61 |
| ETH | 40 | 57.5% | $1,355 | 1.94 | -4.1% | $33.87 | 1.99 |
| HYPE | 97 | 29.9% | $-1,761 | -2.16 | -17.6% | $-18.16 | 0.61 |
| **Combined** | **160** | — | **$-870** | — | — | — | — |

Fees total: $823.

## Verdict

Loser — ETH leg is green (PF 1.99) but BTC/HYPE drag it under; inconsistent.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
