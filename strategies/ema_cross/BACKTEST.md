# EMA Crossover — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), FULL cached range: BTC/ETH 5,379 bars, 2026-03-14 22:00 UTC →
2026-10-25 00:00 UTC; HYPE 5,377 bars, 2026-03-15 00:00 UTC →
2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=30 bars.

## Results (shipped config: EMA(9)/EMA(21) cross, opposite-cross
exit, 2xATR stop, 2.5xATR trail, 168-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 241 | 29.9% | -$2,218 | -22.2% | -1.52 | -25.8% | -$9.20 | 0.78 |
| ETH | 269 | 30.1% | -$983 | -9.8% | -0.55 | -27.1% | -$3.65 | 0.91 |
| HYPE | 219 | 33.8% | +$1,147 | +11.5% | +0.86 | -16.0% | +$5.24 | 1.11 |
| **Combined** | **729** | — | **-$2,054** | — | — | — | -$2.82 | — |

Fees: BTC $2,464, ETH $2,359, HYPE $1,320 (total $6,143).
Exits: 552 stop / 177 signal — three quarters of all trades die on
the stop, which is the crossover's signature: the cross fires, the
trend doesn't follow, the stop takes it.

## Verdict: loser, with one green leg that doesn't save it

The bare crossover loses on BTC and ETH by wide margins and only
prints green on HYPE (+$1,147, PF 1.11) — and HYPE's win rate (33.8%)
is barely above the other two, so the green leg is carried by a few
large winners, not a better signal. Combined -$2,054 on 729 trades is
a real result, not noise: the crossover fires often, wins less than
a third of the time, and the stop does most of the exiting. Nothing
here approaches a live gate.

## Mechanism

EMA(9) vs EMA(21) cross, opposite-cross exit, 2xATR stop, 2.5xATR
chandelier trail, 168-bar max hold. All params fixed a priori; no
optimization.

Source: moving-average crossover (Murphy, Technical Analysis of the
Financial Markets).

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
