# volume_spike_breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`): BTC/ETH 5,384 bars,
2026-03-14 22:00 UTC → 2026-10-25 00:00 UTC; HYPE 5,382 bars,
2026-03-15 00:00 UTC → 2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop (VCP: 1.5xATR),
3x leverage cap, $10k start, long/short except VCP (long only).

## Results (shipped config: 20-bar breakout + volume >2x avg; 20-bar, 2x volume)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 159 | 28.3% | $-1,457 | -1.04 | -20.6% | $-9.17 | 0.80 |
| ETH | 141 | 37.6% | $635 | 0.56 | -14.5% | $4.50 | 1.09 |
| HYPE | 143 | 37.1% | $468 | 0.45 | -13.7% | $3.27 | 1.07 |
| **Combined** | **443** | — | **$-354** | — | — | — | — |

Fees total: $3,641.

## Verdict

Near-flat loser — volume confirmation helps (ETH/HYPE green) but BTC drags it under; not an edge.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
