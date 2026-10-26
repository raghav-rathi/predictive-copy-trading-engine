# supertrend_adx_filter — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`): BTC/ETH 5,384 bars,
2026-03-14 22:00 UTC → 2026-10-25 00:00 UTC; HYPE 5,382 bars,
2026-03-15 00:00 UTC → 2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop (VCP: 1.5xATR),
3x leverage cap, $10k start, long/short except VCP (long only).

## Results (shipped config: Supertrend flip with ADX(14)>25; ST(10,3), ADX>25)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 43 | 27.9% | $-764 | -1.14 | -9.8% | $-17.76 | 0.66 |
| ETH | 49 | 28.6% | $-1,559 | -2.58 | -17.7% | $-31.81 | 0.43 |
| HYPE | 30 | 40.0% | $238 | 0.47 | -6.2% | $7.92 | 1.15 |
| **Combined** | **122** | — | **$-2,085** | — | — | — | — |

Fees total: $952.

## Verdict

Loser — the ADX gate cuts trades to 122 but does not save the flips.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
