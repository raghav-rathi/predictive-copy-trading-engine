# Marubozu Breakout — Backtest

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
| BTC | 138 | 34.1% | $-1,223 | -0.97 | -14.8% | $-8.87 | 0.81 |
| ETH | 111 | 33.3% | $-332 | -0.23 | -18.4% | $-2.99 | 0.93 |
| HYPE | 150 | 35.3% | $418 | 0.42 | -13.2% | $2.79 | 1.07 |
| **Combined** | **399** | — | **$-1,138** | — | — | — | — |

Fees total: $3,179.

## Verdict

Loser — conviction candles on 1h bars are continuation as often as reversal; BTC/ETH red, HYPE thin green.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
- Body >= 90% of range is Nison's strict marubozu; loosening it would just admit ordinary strong bars and more churn.
