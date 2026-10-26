# bollinger_band_walk — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`): BTC/ETH 5,384 bars,
2026-03-14 22:00 UTC → 2026-10-25 00:00 UTC; HYPE 5,382 bars,
2026-03-15 00:00 UTC → 2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop (VCP: 1.5xATR),
3x leverage cap, $10k start, long/short except VCP (long only).

## Results (shipped config: first close outside BB(20,2), exit at mid-band; 20/2.0)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 214 | 32.2% | $-879 | -0.49 | -21.9% | $-4.11 | 0.91 |
| ETH | 199 | 36.2% | $706 | 0.58 | -15.2% | $3.55 | 1.08 |
| HYPE | 213 | 36.2% | $215 | 0.26 | -14.9% | $1.01 | 1.02 |
| **Combined** | **626** | — | **$43** | — | — | — | — |

Fees total: $5,269.

## Verdict

Flat — +$43 combined; the walk is a coin flip on this window.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
