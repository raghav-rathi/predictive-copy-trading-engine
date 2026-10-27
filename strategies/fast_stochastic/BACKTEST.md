# Lane Fast Stochastic — Backtest

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
| BTC | 350 | 35.7% | $-4,537 | -3.43 | -47.0% | $-12.96 | 0.68 |
| ETH | 319 | 38.9% | $-2,798 | -1.92 | -35.1% | $-8.77 | 0.80 |
| HYPE | 409 | 38.4% | $-3,594 | -2.49 | -40.4% | $-8.79 | 0.77 |
| **Combined** | **1078** | — | **$-10,930** | — | — | — | — |

Fees total: $6,644.

## Verdict

Loser — zone crosses whipsaw on 1h bars, as with slow_stochastic before it; removing the %K smoothing makes it worse, not better.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
- No sweep adopted: the (14,3) Lane spec is the shipped config; faster/slower %D variants would be in-sample selection on a losing base.
