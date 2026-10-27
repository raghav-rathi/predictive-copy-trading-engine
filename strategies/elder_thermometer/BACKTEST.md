# Elder Market Thermometer — Backtest

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
| BTC | 302 | 40.7% | $-4,849 | -4.17 | -49.1% | $-16.06 | 0.54 |
| ETH | 302 | 47.0% | $-2,706 | -2.01 | -33.8% | $-8.96 | 0.77 |
| HYPE | 237 | 40.9% | $-2,560 | -1.96 | -37.3% | $-10.80 | 0.76 |
| **Combined** | **841** | — | **$-10,114** | — | — | — | — |

Fees total: $5,516.

## Verdict

Loser — quiet-range prints after trends are as often continuation pauses as reversals; the thermometer adds nothing over a bare range filter.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
- The 0.6 quiet threshold and the 20-bar average are Elder-flavoured choices, not Elder's published rule verbatim; the concept, not the exact threshold, is what failed.
