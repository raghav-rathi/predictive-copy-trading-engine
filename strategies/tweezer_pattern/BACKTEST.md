# tweezer_pattern — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`): BTC/ETH 5,384 bars,
2026-03-14 22:00 UTC → 2026-10-25 00:00 UTC; HYPE 5,382 bars,
2026-03-15 00:00 UTC → 2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop (VCP: 1.5xATR),
3x leverage cap, $10k start, long/short except VCP (long only).

## Results (shipped config: equal high/low within 0.15% + close back inside; 0.15% tolerance)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 1851 | 24.5% | $-9,573 | -14.56 | -95.7% | $-5.17 | 0.47 |
| ETH | 1562 | 26.6% | $-8,615 | -9.29 | -86.9% | $-5.52 | 0.60 |
| HYPE | 1029 | 34.9% | $-4,965 | -3.50 | -51.2% | $-4.82 | 0.77 |
| **Combined** | **4442** | — | **$-23,152** | — | — | — | — |

Fees total: $18,183.

## Verdict

Structural loser — equal-extreme bars are everywhere on 1h data (4,442 trades) and the signal is noise.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
