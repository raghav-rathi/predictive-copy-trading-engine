# Hammer / Shooting Star — Backtest

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
| BTC | 160 | 36.9% | $-2,105 | -1.98 | -27.3% | $-13.16 | 0.72 |
| ETH | 148 | 41.2% | $-514 | -0.29 | -16.3% | $-3.48 | 0.92 |
| HYPE | 119 | 38.7% | $428 | 0.49 | -9.2% | $3.60 | 1.08 |
| **Combined** | **427** | — | **$-2,191** | — | — | — | — |

Fees total: $3,498.

## Verdict

Loser — hammers at 3-bar trend extremes lose on BTC/ETH; the HYPE leg (+$428) is the only green print and does not cover the book.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
- Stricter than pin_bar_reversal (trend + body-position rules) yet still loses: single-candle location patterns need the structure context the mechanized version drops.
