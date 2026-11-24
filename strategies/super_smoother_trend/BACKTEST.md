# SuperSmoother Trend — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, local cache only
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), batch-45 frozen window ms
`[1773525600000, 1795525200000)` (2026-03-14 22:00 UTC →
2026-11-24 14:00 UTC exclusive; last bar 13:00 UTC): 6,111 bars
BTC/ETH, 6,109 HYPE (HYPE's first bar is 2026-03-15 00:00 UTC).
Run with the pinned runner `scripts/run_pinned_backtest45.py`
(reads cache only, never hits the API, never extends the window).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start per coin. WARMUP=60 bars.

Distinct from the shipped `ehlers_supersmoother` strategy
(price-vs-filter(20) cross with a slope gate): this one is a
dual-filter cross, fast SS(10) vs slow SS(30), with no slope gate.

## Results (shipped config: SS(10) fast + SS(30) slow, long on fast
crossing above slow, short on fast crossing below slow, exits on
the opposite cross, 2xATR stop, 3xATR trail, 60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 489 | 31.70% | -$2,557.31 | -25.20% | -1.14 | -41.20% | -$5.23 | 0.85 | $4,234.18 |
| ETH | 525 | 28.57% | -$4,504.89 | -44.82% | -2.49 | -51.01% | -$8.58 | 0.74 | $3,212.74 |
| HYPE | 472 | 36.23% | +$3,236.60 | +33.41% | +1.47 | -15.00% | +$6.86 | 1.15 | $2,680.22 |
| **Combined** | **1,486** | **32.03%** | **-$3,825.60** | — | — | — | **-$2.57** | — | **$10,127.13** |

## Verdict: loser on BTC and ETH, winner on HYPE only — a mixed bag that nets out negative

Combined -$3,825.60 on 1,486 trades, win rate 32.03%, profit
factor 0.74–0.85 on BTC/ETH. The crossover premise does not pay
on the two majors: entries bleed into the 2xATR stop (MaxDD
-41.20% BTC, -51.01% ETH) and the opposite-cross exit closes
whatever is left. HYPE is the exception — +$3,236.60, PF 1.15,
Sharpe +1.47, MaxDD only -15.00% — the one coin where the
smoother actually rode trends instead of chopping. With 472
trades behind it, the HYPE win is real sample, not a fluke
handful — but it is one coin out of three, and it does not
survive aggregation. The extra 10 days vs the Nov-14 refresh
window improved the combined net from -$5,180 to -$3,825.60
(HYPE +$1,792 → +$3,236.60) without changing the verdict.

The honest nuance: gross of fees the book is +$6,301.53
(BTC +$1,676.87, ETH -$1,292.16, HYPE +$5,916.82) — i.e. the
signal is roughly *zero-edge to slightly positive* before
costs, and $10,127.13 of fees turn it into a loser. The
crossover fires far too often (1,486 trades in 8.5 months,
~6/day across coins) for a trend system: most crosses are
chop, and the fee drag on that volume is the story.

## Calibration note

Shipped the specified SS(10)/SS(30). A (5,20)/(10,30)/(20,50)
fast/slow sweep re-run on this same batch-45 window is in
CALIBRATION.md: (5,20) is catastrophic everywhere (combined
-$17,990.52, BTC MaxDD -80.36%); (20,50) is least-bad combined
(-$349.00) and roughly breakeven on ETH (+$173.49) and positive
on HYPE (+$1,424.77) — but that is an in-sample observation,
not a justification. The (10,30) config was fixed before any
backtest was run; no in-sample adoption.

## Mechanism

Ehlers SuperSmoother, 2-pole Butterworth low-pass on close:
a1 = exp(-1.414*pi/n), b1 = 2*a1*cos(1.414*pi/n), c2 = b1,
c3 = -a1^2, c1 = 1 - c2 - c3, filt[i] = c1*(P[i]+P[i-1])/2 +
c2*filt[i-1] + c3*filt[i-2] (explicit loop, seeded with price).
Fast SS(10) vs slow SS(30): long when fast crosses above slow,
short when fast crosses below slow, exit on the opposite cross.
2xATR hard stop, 3xATR chandelier trail, 60-bar max hold.

Source: John F. Ehlers, "Cybernetic Analysis for Stocks and
Futures" (2004) — SuperSmoother, author's own paper with the
exact code listing:
https://www.mesasoftware.com/papers/UltimateSmoother.pdf

## Audit note (batch 45 refresh)

No code changes were needed. Full re-audit on the batch-45
refresh: the recursion matches Ehlers' published code listing
exactly (coefficients a1/b1/c1/c2/c3 and the
`c1*(P+P[1])/2 + c2*filt[1] + c3*filt[2]` form, seeded with
price for the first bars, exactly as in the source paper);
`crossed_above`/`crossed_below` compare only bars i and i-1;
no NaN anywhere; and the truncation test proves no lookahead
(filter/signal values at bar j are identical whether computed
on the full series or on the series truncated at j). All 13
unit tests pass.

## Limitations

- Single 8.5-month crypto window; the window includes the early-Nov
  selloff, which dominates the BTC/ETH drawdowns.
- 1,486 trades at 32.03% win rate — high trade count, thin edge;
  the gross-of-fees book is near zero, so the verdict hinges on
  costs, not on the signal being strongly wrong.
- HYPE-only win does not generalize: the same config loses
  -$2,557.31 and -$4,504.89 on the two majors.
- The (20,50) calibration read is in-sample only; never tune the
  shipped periods on this window.
- Funding unmodeled; next-bar-open execution vs idealized entry.
