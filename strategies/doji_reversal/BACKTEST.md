# Doji Reversal — Backtest

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
| BTC | 121 | 33.1% | $-2,200 | -2.21 | -23.2% | $-18.18 | 0.64 |
| ETH | 130 | 41.5% | $2,201 | 1.81 | -15.3% | $16.93 | 1.35 |
| HYPE | 147 | 35.4% | $-649 | -0.45 | -18.0% | $-4.41 | 0.90 |
| **Combined** | **398** | — | **$-648** | — | — | — | — |

Fees total: $3,085.

## Verdict

Loser — combined -$648, but the ETH leg (+$2,201, Sharpe 1.81) is the batch's best single leg; BTC drags the book under. Coin-regime noise, not a system.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
- The 10-bar extreme + trend filter is the whole signal; mid-range dojis are excluded by construction, so the result is not a dilution artifact.
