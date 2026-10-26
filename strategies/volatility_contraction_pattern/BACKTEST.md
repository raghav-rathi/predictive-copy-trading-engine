# volatility_contraction_pattern — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`): BTC/ETH 5,384 bars,
2026-03-14 22:00 UTC → 2026-10-25 00:00 UTC; HYPE 5,382 bars,
2026-03-15 00:00 UTC → 2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop (VCP: 1.5xATR),
3x leverage cap, $10k start, long/short except VCP (long only).

## Results (shipped config: uptrend + falling ATR + tight range + breakout on volume; SMA50, ATR ratio <1, range <2%)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 37 | 27.0% | $393 | 0.47 | -12.5% | $10.63 | 1.18 |
| ETH | 22 | 45.5% | $772 | 0.91 | -6.8% | $35.09 | 1.67 |
| HYPE | 7 | 14.3% | $5 | 0.04 | -3.3% | $0.70 | 1.01 |
| **Combined** | **66** | — | **$1,170** | — | — | — | — |

Fees total: $1,203.

## Verdict

Thin green — only VCP leg set in the batch is positive on all three coins, but 66 trades is too thin to call anything.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
