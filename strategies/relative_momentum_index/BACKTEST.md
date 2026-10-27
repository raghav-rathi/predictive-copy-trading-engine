# Relative Momentum Index — Backtest

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
| BTC | 209 | 33.5% | $-933 | -0.60 | -20.6% | $-4.46 | 0.90 |
| ETH | 237 | 30.4% | $309 | 0.32 | -21.5% | $1.30 | 1.03 |
| HYPE | 224 | 33.0% | $970 | 0.74 | -13.4% | $4.33 | 1.09 |
| **Combined** | **670** | — | **$346** | — | — | — | — |

Fees total: $5,956.

## Verdict

Flat — +$346 combined on 670 trades, expectancy $0.52/trade, with BTC red and ETH/HYPE green. RMI smooths RSI but does not beat it.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
- RMI(14,1) == RSI(14) is asserted in the unit tests, so the implementation is verified; the edge, not the code, is missing.
