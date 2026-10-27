# Bollinger Bandwidth Breakout — Backtest

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
| BTC | 112 | 29.5% | $-1,741 | -1.91 | -23.2% | $-15.54 | 0.66 |
| ETH | 111 | 34.2% | $-1,459 | -1.55 | -21.7% | $-13.15 | 0.70 |
| HYPE | 110 | 37.3% | $661 | 0.65 | -7.3% | $6.01 | 1.15 |
| **Combined** | **333** | — | **$-2,539** | — | — | — | — |

Fees total: $2,713.

## Verdict

Loser — the expansion filter does not save the band breakout; only the HYPE leg is green and it does not cover the majors' losses.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
- Bandwidth expansion is a weaker confirmation than the squeeze condition (BB inside Keltner) that already ships; band breakouts on 1h remain chop victims.
