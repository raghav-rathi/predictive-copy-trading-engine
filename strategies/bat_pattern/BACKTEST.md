# Bat Harmonic Pattern — Backtest

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
| BTC | 1 | 0.0% | $-46 | -1.12 | -0.5% | $-45.61 | 0.00 |
| ETH | 1 | 0.0% | $-40 | -0.54 | -1.1% | $-40.39 | 0.00 |
| HYPE | 0 | 0.0% | $0 | 0.00 | 0.0% | $0.00 | 0.00 |
| **Combined** | **2** | — | **$-86** | — | — | — | — |

Fees total: $17.

## Verdict

Inconclusive — -$86 on 2 trades (1 BTC, 1 ETH, 0 HYPE). The Bat ratio stack almost never completes on 1h bars, same as the Gartley before it.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
- The ratio stack is Carney's published Bat (AB 38.2–50%, CD 161.8–261.8%, AD 88.6% ±6%); the Gartley-ratio negative control is asserted in the unit tests, so a Bat fire is genuinely a Bat, not a mislabelled Gartley.
