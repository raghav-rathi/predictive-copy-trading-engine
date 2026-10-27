# Rising / Falling Three Methods — Backtest

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
| BTC | 4 | 25.0% | $-12 | -0.03 | -2.7% | $-3.07 | 0.93 |
| ETH | 6 | 66.7% | $681 | 1.96 | -2.0% | $113.42 | 5.16 |
| HYPE | 3 | 0.0% | $-216 | -1.68 | -2.7% | $-71.94 | 0.00 |
| **Combined** | **13** | — | **$452** | — | — | — | — |

Fees total: $102.

## Verdict

Inconclusive — +$452 on 13 trades in 7 months. The 5-bar containment rule is too strict for 1h crypto to evaluate.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
- Pattern verified on synthetic data; the real-data rarity is the finding, matching the daily-chart problem seen with cup_handle and harmonic_gartley.
