# Wilder Parabolic SAR system — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), pinned window: 2026-03-14 22:00 UTC → 2026-11-22 14:00 UTC
(BTC 6,064 bars, ETH 6,064 bars, HYPE 6,062 bars — HYPE's cache
starts two bars later, at 2026-03-15 00:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=20 bars.

## Results (shipped config: raw Wilder PSAR, AF step 0.02, max
0.20; flip is the entry and the exit; 2xATR harness backstop;
336-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 476 | 34.0% | -$3,682 | -37.0% | -1.68 | -52.5% | -$7.73 | 0.81 |
| ETH | 448 | 33.9% | -$1,984 | -20.1% | -0.69 | -33.0% | -$4.43 | 0.91 |
| HYPE | 542 | 36.9% | -$608 | -5.3% | -0.07 | -23.7% | -$1.12 | 0.97 |
| **Combined** | **1,466** | **35.1%** | **-$6,273** | — | — | — | **-$4.28** | — |

Fees: BTC $4,041, ETH $3,358, HYPE $2,613 (total $10,012).
Exit reasons: 991 flips (signal) vs 475 harness-stop hits —
about a third of all trades were stopped out by the 2xATR
backstop before the SAR could flip. Longs and shorts are
near-exactly balanced (e.g. BTC 238/238): the system is always
in the market, so every flip closes one side and opens the
other.

## Verdict: loser — raw PSAR whipsaws to death on 1h crypto

This is the point of the build, and the answer is unambiguous:
the unfiltered PSAR system loses on all three coins, with
1,466 trades — the largest sample of any batch-44 strategy so
far — so this is not a small-sample fluke. Win rate 34–37%,
profit factor 0.81–0.97, and a -52.5% max drawdown on BTC.

- The mechanism fails exactly where Wilder's system is known
  to fail: sideways, choppy markets. PSAR flips on every
  counter-trend wiggle, and 1h crypto in this window chopped
  hard (BTC lost ~40% from the March highs into the November
  lows with repeated counter-trend rallies). Each flip pays
  the spread twice — once to exit, once to re-enter.
- The one nuance worth recording: **gross of fees the system
  was positive on all three coins** (+$359 BTC, +$1,374 ETH,
  +$2,005 HYPE; +$3,738 combined). The edge, if it exists at
  all, is smaller than the 0.11% round-trip cost at this
  turnover (a flip every ~12 bars). Fees of $10,012 exceed the
  $6,273 net loss. A cheaper venue or a slower SAR (larger AF
  step, or a trend filter that suppresses flips) would be the
  only routes to viability — both are out of scope here; this
  build isolates PSAR's own edge, and on 1h crypto that edge
  does not survive costs.
- HYPE is the least-bad coin (PF 0.97, Sharpe -0.07) because
  its strong trending stretches in 2026 let the SAR ride; BTC
  is the worst (Sharpe -1.68) because its chop was the most
  expensive.

Stated plainly: do not trade raw PSAR on 1h crypto. The
existing psar_macd strategy exists precisely because PSAR
needs an agreement filter — this backtest is the evidence for
why.

## Mechanism

LONG while price is above the SAR, SHORT while below it; the
SAR flip closes one side and opens the other (AF step 0.02,
max 0.20, seeded LONG from bar 0 with SAR = low[0] — the seed
emits no entry; the first trade is the first genuine flip).
2xATR(14) harness stop is a backstop only; 336-bar max hold.
All params fixed a priori from Wilder (1978); no optimization.

Source: J. Welles Wilder, *New Concepts in Technical Trading
Systems* (1978) — https://en.wikipedia.org/wiki/Parabolic_SAR

## Limitations

- Single 8-month crypto window, heavily trending down into
  November; funding unmodeled; next-bar-open execution vs
  idealized flip.
- The gross-of-fees positive is not an edge claim: it is
  within noise for a system whose net is negative on every
  coin, and it depends on the 2xATR stop cutting losers short.
- Never tune the shipped parameters on this window — least of
  all the AF step/max, which directly control flip frequency.
