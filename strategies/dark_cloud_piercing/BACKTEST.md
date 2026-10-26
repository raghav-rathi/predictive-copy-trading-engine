# dark_cloud_piercing — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`): BTC/ETH 5,384 bars,
2026-03-14 22:00 UTC → 2026-10-25 00:00 UTC; HYPE 5,382 bars,
2026-03-15 00:00 UTC → 2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop (VCP: 1.5xATR),
3x leverage cap, $10k start, long/short except VCP (long only).

## Results (shipped config: open beyond prior close + close past midpoint (gap adapted); midpoint rule)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 121 | 36.4% | $-2,147 | -2.32 | -21.5% | $-17.74 | 0.61 |
| ETH | 140 | 28.6% | $-2,178 | -2.32 | -26.0% | $-15.56 | 0.65 |
| HYPE | 167 | 37.1% | $-1,350 | -1.00 | -20.8% | $-8.08 | 0.81 |
| **Combined** | **428** | — | **$-5,675** | — | — | — | — |

Fees total: $2,873.

## Verdict

Loser — the gap adaptation makes it fire (428 trades) and it loses on every coin.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
