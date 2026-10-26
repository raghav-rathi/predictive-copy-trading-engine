# volatility_breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`): BTC/ETH 5,384 bars,
2026-03-14 22:00 UTC → 2026-10-25 00:00 UTC; HYPE 5,382 bars,
2026-03-15 00:00 UTC → 2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop (VCP: 1.5xATR),
3x leverage cap, $10k start, long/short except VCP (long only).

## Results (shipped config: prior close +/- 0.5 x prior range; Williams K=0.5)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 1194 | 26.6% | $-8,971 | -10.35 | -90.0% | $-7.51 | 0.52 |
| ETH | 1134 | 28.0% | $-7,695 | -6.40 | -77.8% | $-6.79 | 0.64 |
| HYPE | 1171 | 30.7% | $-7,346 | -6.57 | -73.8% | $-6.27 | 0.64 |
| **Combined** | **3499** | — | **$-24,013** | — | — | — | — |

Fees total: $13,619.

## Verdict

Structural loser — prior-bar range levels fire constantly on 1h bars (3,499 trades) and bleed on every coin.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
