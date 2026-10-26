# morning_evening_star — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`): BTC/ETH 5,384 bars,
2026-03-14 22:00 UTC → 2026-10-25 00:00 UTC; HYPE 5,382 bars,
2026-03-15 00:00 UTC → 2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop (VCP: 1.5xATR),
3x leverage cap, $10k start, long/short except VCP (long only).

## Results (shipped config: large candle + small star + midpoint close (gap adapted); big >1%, star <0.3%)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 2 | 50.0% | $137 | 0.78 | -1.6% | $68.30 | 3.35 |
| ETH | 8 | 75.0% | $741 | 2.09 | -2.0% | $92.58 | 5.00 |
| HYPE | 19 | 31.6% | $469 | 1.03 | -4.2% | $24.66 | 1.46 |
| **Combined** | **29** | — | **$1,346** | — | — | — | — |

Fees total: $137.

## Verdict

Thin green — 29 trades, all three legs positive, but far too few trades to be a finding.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
