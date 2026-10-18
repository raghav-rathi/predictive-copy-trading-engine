# Williams Alligator + Fractal — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-18
(~5,224 bars each). Note: the batch brief's ms window constants were stamped
2025 (they filtered to an empty frame against 2026 data); corrected by +365d
to the intended 2026 window. Cache rows deduplicated in-memory (5 identical
overlap rows per file from cache-extension appends; cache files untouched).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: Alligator SMMA(13/8/5) of median shifted 8/5/3, k=2 fractal breakout entries with teeth filter + awake fan, exit on opposite break or lips/teeth sleep cross, 1.5xATR stop, 72-bar max hold, WARMUP=80)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 152 | 27.6% | -$2,653 | -26.5% | -1.48 | -29.2% | -$17.46 | 0.72 |
| ETH | 168 | 24.4% | -$1,840 | -18.4% | -0.67 | -29.8% | -$10.95 | 0.83 |
| HYPE | 166 | 27.7% | -$1,779 | -17.8% | -0.89 | -24.8% | -$10.72 | 0.83 |
| **Combined** | **486** | **26.6%** | **-$6,273** | — | — | — | -$12.91 | — |

## Verdict: LOSER

Loses on every coin: −18% to −27%, profit factors 0.72–0.83, win rates
24–28%. The fractal-breakout entries are late by construction — the pivot
needs 2 confirming bars, the Alligator lines lag 3–8 bars by design, and
the "awake fan" filter means entries only fire mid-move. On 1h crypto the
move is usually over by then: entries buy the tail of the leg and the
lips/teeth sleep cross exits into the reversal. The 2.0-stop sweep
(CALIBRATION.md) lifts BTC near breakeven but leaves ETH/HYPE negative —
coin-inconsistent, i.e. noise, not edge.

## Calibration note

Shipped exactly the specified parameters (SMMA 13/8/5 shifted 8/5/3,
k=2 fractals, teeth filter, awake fan, opposite-break + sleep exits,
1.5xATR stop, 72-bar max hold, WARMUP=80). The one-variant sweep (stop
1.5 → 2.0xATR) is reported in CALIBRATION.md — it helps BTC only. No
further tuning attempted; the entries are structurally late, not
mis-sized.

## Mechanism

Median = (h+l)/2. Alligator lines = Wilder SMMA of median: jaw SMMA(13)
known with an 8-bar lag, teeth SMMA(8) with a 5-bar lag, lips SMMA(5) with
a 3-bar lag (shift applied after smoothing — no lookahead). Awake =
lips > teeth > jaw (longs) / lips < teeth < jaw (shorts). Fractals: strict
5-bar (k=2) pivots — buy fractal = high[i] above the 2 bars on each side;
the pivot is only confirmed 2 bars later, so the traded level is the raw
pivot shifted by k and forward-filled. Long when a confirmed buy-fractal
high breaks (close > level) AND the level is above the teeth AND the
Alligator is awake; mirror for shorts. Exits: opposite fractal break, or
the Alligator falling asleep (lips crosses below teeth for longs, above
for shorts). 1.5xATR hard stop — the harness's approximation of a
fractal-extreme stop (see risk.py) — 72-bar max hold, no trailing, no
target.

Source: Bill Williams, *Trading Chaos* — Profitunity Alligator + fractal
system —
https://forexstrategiesresources.com/metatrader-trading-system-ii/239-profitunity-chaos-trading-system-by-bill-williams/

## Limitations

- Single 7-month crypto window; no bull-market sample.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs idealized signal-bar entry.
- Stop is 1.5xATR, not the true Williams fractal-extreme stop the system
  calls for (harness limitation, documented in risk.py).
- 1h bars only; Williams designed the system for daily+ bars where the
  Alligator's lags are proportionally smaller.
