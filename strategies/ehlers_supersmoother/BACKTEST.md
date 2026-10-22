# SuperSmoother Trend — Backtest

**Data:** local Hyperliquid 1h candle cache, BTC + ETH + HYPE, sliced to
the batch window 2026-03-14 00:00 UTC → 2026-10-21 23:59 UTC
(ms `[1773446400000, 1792627199000)`; actual data ends 2026-10-21
13:00 UTC, the last cached candle for all three coins): 5,301 bars
BTC/ETH, 5,299 HYPE. Fully offline — no API calls, funding not modeled.
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=80 bars.

## Results (shipped config: SuperSmoother(20), long on a cross-above
with a rising filter, short on a cross-below with a falling filter,
exits on the opposite cross, 2xATR stop, 2xATR trail, 150-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 307 | 24.1% | -$3,482 | -34.8% | -3.83 | -39.2% | -$11.34 | 0.60 |
| ETH | 304 | 27.3% | -$1,425 | -14.2% | -1.32 | -23.6% | -$4.69 | 0.83 |
| HYPE | 303 | 27.4% | -$2,141 | -21.4% | -2.42 | -21.6% | -$7.06 | 0.72 |
| **Combined** | **914** | **26.3%** | **-$7,047** | — | — | — | -$7.71 | — |

## Verdict: an honest loser — the filter-cross mechanism has no edge on 1h crypto

Combined -$7,047 across 914 trades, and every coin is red: BTC
-$3,482 (PF 0.60, Sharpe -3.83, -39.2% drawdown), ETH -$1,425 (PF
0.83), HYPE -$2,141 (PF 0.72). The win rate sits at 24–27% everywhere
with roughly 1:1 realized R:R (2xATR stop vs cross-driven exits) —
that arithmetic cannot beat costs, and the expectancy (-$7.71/trade)
is negative before fees are even the story (fees $3,028 BTC, $2,583
ETH, $1,300 HYPE). Exits are dominated by signal crosses (556) and
stops (358); the 2xATR trail essentially never locks in a runner, and
the 150-bar cap is never reached.

The mechanism's problem is visible on the charts: a cross of close vs
a 20-bar low-pass filter fires when the leg is already mostly spent,
and the slope gate — which genuinely helps (see the diagnostic
below) — leaves only the late confirmations. Trend-crossing a smooth
filter on 1h crypto is a whipsaw machine in chop and a late-comer in
trends; this run does both.

Diagnostic: the same pipeline with the slope gate removed (raw
crosses only) loses roughly twice as much — BTC -$8,313 (1,022
trades), ETH -$5,972 (1,008), HYPE -$6,615 (993). The gate is doing
real work, cutting the raw-cross bleed roughly in half. The residual
loss is the cross mechanism itself, not the gate.

## Calibration note

Period was fixed at 20 a priori (Ehlers' canonical cutoff) before any
backtest ran. A 10/20/40 period sweep is in CALIBRATION.md: every
period × coin cell is negative — the sweep moves the size of the
loss, not its sign. No in-sample selection is possible from a sweep
that is red everywhere, and none was applied.

## Mechanism

SuperSmoother(20): a1 = exp(-1.414π/20), b1 = 2·a1·cos(1.414·180/20°),
c2 = b1, c3 = -a1², c1 = 1 - c2 - c3;
filt[i] = c1·(c[i]+c[i-1])/2 + c2·filt[i-1] + c3·filt[i-2].
Long when close crosses above the filter while it is rising; short on
a cross below while it is falling. Exits are the opposite cross,
ungated. 2xATR hard stop, 2xATR chandelier trail, 150-bar max hold.

Source: SuperSmoother (John Ehlers) —
https://forex-station.com/post1295578265.html

## Limitations

- Single 7-month crypto window; 914 trades is a decent sample, but it
  is one regime and the sign is uniformly negative across it.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- The filter's half-lag advantage (verified on synthetic step
  response) does not translate into a tradable edge at this
  timeframe — smoothing helps the eye, not the ledger.
- Never tune the shipped period on this window (see CALIBRATION.md).
