# ICT Inducement → Sweep → MSS Entry — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms).
**Window:** 2026-03-14 22:00 UTC → 2026-11-21 14:00 UTC
(BTC/ETH 6,040 bars, HYPE 6,038 bars).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=100 bars.

## Results (shipped config: full sequence, 1.5xATR displacement,
3-bar swing confirmation, 70.5% OTE, 24-bar expiry, 2xATR stop,
4xATR target, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 0 | — | $0 | 0.0% | 0.00 | 0.0% | — | — |
| ETH | 0 | — | $0 | 0.0% | 0.00 | 0.0% | — | — |
| HYPE | 0 | — | $0 | 0.0% | 0.00 | 0.0% | — | — |
| **Combined** | **0** | **—** | **$0** | — | — | — | — | — |

Fees: $0.

## Verdict: inconclusive — zero trades, nothing to judge

The full sequence never completes once in 18,118 bars across
three coins. That is the result, stated plainly: there is no
evidence here for or against the ICT thesis, because the strategy
never traded. This is a thin sample in the extreme — not a small
sample, an empty one — and it must not be quoted as a win, a
loss, or a refutation.

## Where the sequence dies (diagnostic funnel)

An instrumented rerun of the same state machine counts how far
setups get per coin (displacement → OB → inducement → sweep →
MSS → displacement+FVG → OTE fire):

| Stage | BTC | ETH | HYPE |
|---|---|---|---|
| Displacement bars (idle) | 79 | 81 | 80 |
| OB marked | 79 | 81 | 80 |
| Inducement set | 52 | 48 | 55 |
| Sweep into POI | 19 | 25 | 27 |
| MSS (+ displacement/FVG) | 2 | 1 | 1 |
| OTE retracement within 24 bars | 0 | 0 | 0 |

Two things stand out. First, the early stages are not rare at
all — displacements, inducements and even full sweeps into the POI
happen dozens of times per coin. The sequence is selective, not
absent. Second, the binding constraint is the last two steps
together: after a genuine sweep and MSS, price almost never comes
back 70.5% of the displacement leg within 24 bars — the four
setups that reached the OTE stage (2 BTC, 1 ETH, 1 HYPE) all
expired unfilled. A 70.5% retracement of an impulsive leg is a
deep pullback, and on 1h crypto bars the displacement leg usually
just runs.

That funnel is also why the rules were NOT loosened: widening the
OTE band, shortening the displacement threshold or dropping the
FVG requirement would manufacture trades, but they would no
longer be the ICT sequence — they would be a different strategy
tuned to produce a sample on this window. The honest conclusion
is that the full sequence, as mechanically specified, is
effectively untradeable at 1h resolution in this window; a real
verdict would need a longer window, lower timeframes (where the
sequence is actually drawn by ICT traders), or a deliberately
different specification validated out-of-sample.

## Mechanism

Order block from a displacement leg (last opposing candle, 10-bar
lookback); first 3-bar-confirmed swing low/high above the OB top /
below the OB bottom as inducement; sweep = close beyond the
inducement extreme into the OB zone; MSS = close beyond the minor
structure high/low, confirmed by a displacement bar (range >
1.5xATR(14), strong close) leaving an FVG; entry at the 70.5%
OTE retracement of the displacement leg, 24-bar expiry, POI
failure drops the setup. 2xATR stop, 4xATR target, 72-bar max
hold. All params fixed a priori; no optimization.

Sources: ForexMT4Indicators, "Inducement in ICT Trading
Explained" (https://forexmt4indicators.com/what-is-inducement/);
session/killzone variant (https://www.mql5.com/en/blogs/post/750916,
not implemented).

## Limitations

- 0 trades: every performance statistic is undefined; do not
  quote this backtest as evidence for or against the strategy.
- Single 8-month window, three coins, 1h bars; funding unmodeled;
  next-bar-open execution vs the idealized limit fill at the OTE
  level (the harness fills at the next bar's open, which can be
  away from the OTE level after a fast touch).
- The 2xATR stop / 4xATR target approximate "beyond the POI" /
  "2R to the next liquidity pool" (see CALIBRATION.md).
- Never tune the shipped parameters on this window.
