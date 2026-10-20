# OU Half-Life Z-Score Mean Reversion — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-20 13:00 UTC
(ms `[1773446400000, 1792501200000)`): 5,271 bars BTC/ETH (cache starts
2026-03-14 02:00 UTC), 5,269 HYPE (HYPE history starts 2026-03-15
00:00 UTC). Last bar 2026-10-20 12:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2.5xATR stop, 3x leverage cap,
$10k start. WARMUP=120 bars.

## Results (shipped config: dev = log(c) − SMA(log(c), 50), per-bar
AR(1) on trailing 100 dev values, HL = −ln2/θ valid for θ < 0 and
5 ≤ HL ≤ 120, z = dev/std(dev, 50), long z < −2 / short z > 2, exits
at z = 0, 2.5xATR stop, no target, 200-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 161 | 42.2% | -$3,484 | -34.8% | -3.30 | -39.0% | -$21.64 | 0.60 |
| ETH | 152 | 48.0% | -$1,603 | -16.0% | -1.38 | -24.6% | -$10.55 | 0.81 |
| HYPE | 138 | 39.9% | -$3,025 | -30.2% | -3.21 | -33.6% | -$21.92 | 0.59 |
| **Combined** | **451** | **43.5%** | **-$8,112** | — | — | — | -$17.99 | 0.67 |

## Verdict: clear loser — worst book of the batch

451 trades, −$8,112 combined, Sharpe −3.3 on BTC, max drawdown −39% on
the BTC leg. This is not noise: the strategy trades *into* deviations
from a trailing mean that chases price, and in a 7-month window with
strong directional regimes the deviations keep extending — the z ≥ 0
exit is a fantasy when the anchor itself is moving against the
position. The 2.5xATR stop was supposed to give room; instead it gave
the position room to bleed. Note the mechanism's dirty secret found in
testing: deviations from a trailing SMA are *mechanically*
mean-reverting (the mean chases), so the AR(1) fit reads HL ≈ 15–30 on
pure random walks too — the "valid" gate admits far more than genuine
OU processes. Honest read: the half-life filter does not buy
stationarity, and fading z = ±2 on 1h crypto trends is a consistent
way to lose −$18/trade. Fees ($2,441 combined) amplify, not cause, the
loss.

## Calibration note

Shipped the specified z = ±2.0 entry. A 1.5/2.0/2.5 sweep is in
CALIBRATION.md: every setting loses on every coin; z = ±2.5 is least
negative in-sample (combined −$3,761, ETH PF 0.94 on 102 trades) but
still red everywhere — adopting it would be in-sample selection on a
loser. Keep 2.0 as specified; no threshold rescues the premise.

## Mechanism

Deviation `dev = log(close) − SMA(log(close), 50)`. Each bar fits AR(1)
on the trailing 100 dev values — regressing `dev.diff()` on
`dev.shift(1)` with rolling covariance/variance (causal, O(n)) —
giving slope θ and half-life `HL = −ln(2)/θ`. A bar is tradable only
when θ < 0 (mean-reverting) and 5 ≤ HL ≤ 120 (explosive and
near-unit-root regimes excluded). Z-score `z = dev / rolling_std(dev,
50)`; long when z < −2, short when z > 2; exits when z crosses 0. Risk:
2.5xATR stop, no target, no trailing, 200-bar max hold.

Source: OU half-life mean reversion (luxalgo.com) —
https://www.luxalgo.com/blog/mean-reversion-strategies-for-algorithmic-trading/

## Limitations

- Single 7-month crypto window; 451 trades, deeply negative.
- The HL validity gate admits random-walk deviations (documented in
  testing: trailing-SMA anchors mechanically create HL ≈ 15–30) — it
  filters momentum regimes, not non-stationarity.
- Exits assume the anchor is stationary; in trending regimes the mean
  follows price and the z = 0 exit never arrives before the stop.
- Funding unmodeled; next-bar-open execution vs idealized entry.
