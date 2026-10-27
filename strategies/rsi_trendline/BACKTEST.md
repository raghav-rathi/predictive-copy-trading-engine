# RSI Trendline Break — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`): BTC/ETH 5,440 bars,
2026-03-14 22:00 UTC → 2026-10-27 13:00 UTC; HYPE 5,438 bars.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop,
3x leverage cap, $10k start, long/short.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 374 | 34.8% | $-2,805 | -1.84 | -34.8% | $-7.50 | 0.80 |
| ETH | 392 | 35.2% | $-2,240 | -1.35 | -38.3% | $-5.72 | 0.86 |
| HYPE | 370 | 38.6% | $-2,344 | -1.43 | -25.5% | $-6.34 | 0.84 |
| **Combined** | **1136** | — | **$-7,390** | — | — | — | — |

Fees total: $8,781.

## Verdict

Loser — RSI trendline breaks mark pauses, not reversals, on 1h crypto; win rates 35–39% with steady stop exits.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
- Trendline construction uses confirmed (3-bar) RSI pivots only; unconfirmed pivots would fire earlier but would also be lookahead-adjacent, so they were not used.
