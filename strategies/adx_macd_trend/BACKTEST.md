# ADX + MACD Trend — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), filtered to t >= 1773525600000: BTC/ETH 5,445 bars,
2026-03-14 22:00 UTC → 2026-10-27 13:00 UTC; HYPE 5,443 bars,
2026-03-15 00:00 UTC → 2026-10-27 13:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run, funding off).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=40 bars.

## Results (shipped config: ADX(14) > 25 + DI direction + MACD
cross entry, opposite MACD cross or ADX < 20 exit, 2xATR stop,
2.5xATR trail, 168-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 70 | 25.7% | -$1,397.97 | -13.98% | -1.71 | -19.05% | -$19.97 | 0.58 |
| ETH | 63 | 33.3% | -$960.66 | -9.61% | -1.55 | -15.41% | -$15.25 | 0.62 |
| HYPE | 55 | 30.9% | -$972.04 | -9.72% | -1.87 | -12.98% | -$17.67 | 0.57 |
| **Combined** | **188** | — | **-$3,330.67** | — | — | — | **-$17.72** | — |

Fees: BTC $666.58, ETH $480.00, HYPE $245.25 (total $1,391.83).
Signal entries: BTC 32 long / 38 short, ETH 26 / 37, HYPE 34 / 21.

## Verdict: loser

-$3,330.67 on 188 trades, negative on every coin, profit factors
0.57–0.62 and Sharpes below -1.5 across the board. The ADX gate
does not fix MACD at 1h: entries still arrive late in trends and
whipsaw in ranges that are strong enough to clear ADX 25 without
sustaining direction. Nothing here approaches a live gate.

## Mechanism

ADX(14) > 25 + DI direction + MACD(12, 26, 9) cross entry;
opposite MACD cross or ADX crossing below 20 exit; 2xATR stop,
2.5xATR trail, 168-bar max hold. All params fixed a priori
(textbook Wilder levels); no optimization.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 188 trades is a real sample, and it is uniformly bad — this is
  not a small-sample artifact.
- Never tune the shipped parameters on this window.
