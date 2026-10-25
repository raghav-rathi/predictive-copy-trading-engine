# SMA Crossover — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), FULL cached range: BTC/ETH 5,379 bars, 2026-03-14 22:00 UTC →
2026-10-25 00:00 UTC; HYPE 5,377 bars, 2026-03-15 00:00 UTC →
2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=60 bars.

## Results (shipped config: SMA(20)/SMA(50) cross, opposite-cross
exit, 2xATR stop, 2.5xATR trail, 168-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 123 | 27.6% | -$1,796 | -18.0% | -1.76 | -22.6% | -$14.61 | 0.70 |
| ETH | 133 | 37.6% | -$913 | -9.1% | -0.83 | -12.7% | -$6.86 | 0.83 |
| HYPE | 119 | 37.0% | +$297 | +3.0% | +0.35 | -9.6% | +$2.50 | 1.06 |
| **Combined** | **375** | — | **-$2,412** | — | — | — | -$6.43 | — |

Fees: BTC $1,306, ETH $1,128, HYPE $621 (total $3,055).
Exits: 354 stop / 21 signal — 94% of trades die on the stop. The
slower cross is even more stop-dominated than the fast one: by the
time SMA(20)/SMA(50) confirms, the move is usually over, and the
opposite cross almost never gets to exit a trade first.

## Verdict: loser — slower is not better, it's later

Compared with ema_cross (-$2,054 on 729 trades), the slower pair
loses slightly more (-$2,412) on half the trades, with a worse
per-trade expectancy (-$6.43 vs -$2.82). The HYPE leg is barely
green (+$297, PF 1.06 — noise). The lesson is the same as the fast
cross, sharpened: crossover confirmation lags the move, and on 1h
crypto bars that lag is fatal. Nothing here approaches a live gate.

## Mechanism

SMA(20) vs SMA(50) cross, opposite-cross exit, 2xATR stop, 2.5xATR
chandelier trail, 168-bar max hold. All params fixed a priori; no
optimization.

Source: moving-average crossover (Murphy, Technical Analysis of the
Financial Markets).

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
