# three_soldiers_crows — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`): BTC/ETH 5,384 bars,
2026-03-14 22:00 UTC → 2026-10-25 00:00 UTC; HYPE 5,382 bars,
2026-03-15 00:00 UTC → 2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop (VCP: 1.5xATR),
3x leverage cap, $10k start, long/short except VCP (long only).

## Results (shipped config: 3 strong candles, inside opens; body >0.3%)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 3 | 33.3% | $192 | 0.86 | -1.8% | $64.17 | 3.90 |
| ETH | 5 | 20.0% | $-174 | -0.91 | -2.5% | $-34.73 | 0.30 |
| HYPE | 33 | 24.2% | $-952 | -1.82 | -9.9% | $-28.85 | 0.47 |
| **Combined** | **41** | — | **$-933** | — | — | — | — |

Fees total: $201.

## Verdict

Thin loser — only 41 trades; the strict three-candle structure barely occurs on 1h crypto.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
