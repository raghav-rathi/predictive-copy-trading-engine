# Gaussian Filter Trend — Calibration

## 1. Alpha verification and the fast/slow correction (the main finding)

The brief's alpha formula and 4-pole recursion were checked against
the references before any backtest was run.

**Formula — confirmed as published, no correction needed:**
alpha = (1 − sin(2π/period)) / cos(2π/period). This is Ehlers'
published form (same (1−sin θ)/cos θ structure as the alpha1 used
in this repo's `ehlers_sinewave`), and the 4-pole recursion matches
the published expansion reproduced by Loxx exactly:
f = α⁴·g + 4(1−α)·f[1] − 6(1−α)²·f[2] + 4(1−α)³·f[3] −
(1−α)⁴·f[4]. The coefficient bracket sums to exactly 1 (verified
algebraically and by test: a constant input passes through unchanged
for all pole counts 1–4).

**The correction — the period→speed mapping is inverted:**
alpha INCREASES with period, so the longer-period filter is the
FASTER tracker. Measured (all computed from the shipped code):

| Period | alpha | b = 1−alpha | Group delay 4b/(1−b) | Lag on rising ramp (0.1/bar) | \|H4\| at ω=2π/P |
|---|---|---|---|---|---|
| 10 | 0.5095 | 0.4905 | 3.85 bars | 0.385 below price | 0.337 |
| 30 | 0.8098 | 0.1902 | 0.94 bars | 0.094 below price | 0.975 |

Consequences, all verified numerically:

- On a 720-bar sine wave (3 cycles), the P=10 line crosses ABOVE
  the P=30 line at price TOPS (cross bars 64/304/543, price
  125.0 → falling) and BELOW it at price BOTTOMS (cross bars
  184/423/663, price 75.0 → rising). The brief's literal "P=10
  crosses above P=30 = long" buys tops and sells bottoms.
- On random-walk data the P=30 line's mean |bar-to-bar move| (0.38)
  exceeds the P=10 line's (0.23): the "slow" filter moves more.
- The Wealth-Lab "critical period attenuated by 50% (−3 dB)" claim
  does not hold exactly for the 4-pole cascade with this alpha: a
  30-bar cycle passes the P=30 filter at 97.5% amplitude, while a
  10-bar cycle is attenuated to 33.7% by the P=10 filter. Treat
  "period" as a tuning label, not a precise cutoff, and do not cite
  the −3 dB claim for this implementation.

**Shipped decision:** keep the published formula and the 10/30
periods, but trade the measured crossover direction — long when the
period-30 line crosses above the period-10 line, short on a cross
below. Columns are named by period (`gf_p10`, `gf_p30`) so no
fast/slow label can mislead again. The correction is justified by
the filter mathematics above, NOT by backtest PnL (see §3: the
literal direction also loses).

## 2. Period-pair sensitivity (corrected direction throughout)

Same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 →
2026-10-18, same costs/sizing, 2xATR stop, 3xATR trail, 200-bar max
hold). The sweep re-runs `add_indicators(df, fast=X, slow=Y)` only —
signals and risk are unchanged. Note: in every pair the
longer-period line is the faster tracker (same inversion), so the
sweep compares like with like.

| Periods | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 7/21 | BTC | 446 | 26.9% | -$4,869 | -3.37 | 0.68 | -$10.92 |
| 7/21 | ETH | 452 | 28.3% | -$3,943 | -2.52 | 0.75 | -$8.72 |
| 7/21 | HYPE | 414 | 32.4% | +$803 | +0.55 | 1.05 | +$1.94 |
| 10/30 (shipped) | BTC | 728 | 25.1% | -$7,424 | -6.76 | 0.57 | -$10.20 |
| 10/30 (shipped) | ETH | 729 | 26.6% | -$5,049 | -3.23 | 0.74 | -$6.93 |
| 10/30 (shipped) | HYPE | 696 | 29.7% | -$3,783 | -2.31 | 0.81 | -$5.44 |
| 14/42 | BTC | 1,036 | 23.5% | -$8,289 | -8.55 | 0.56 | -$8.00 |
| 14/42 | ETH | 999 | 25.6% | -$6,568 | -4.92 | 0.68 | -$6.57 |
| 14/42 | HYPE | 1,010 | 28.7% | -$6,174 | -4.75 | 0.69 | -$6.11 |

Combined: 7/21 -$8,010 (1,312 trades), 10/30 -$16,257 (2,153),
14/42 -$21,031 (3,045).

## 3. Literal brief direction, for contrast (P=10 above P=30 = long)

Same data, signals flipped to the brief's literal direction:

| Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|
| BTC | 728 | 58.5% | -$5,593 | -5.44 | 0.65 |
| ETH | 729 | 59.7% | -$5,914 | -5.67 | 0.64 |
| HYPE | 696 | 62.4% | -$3,346 | -2.79 | 0.83 |

Combined -$14,853. The win rate looks respectable (58–62%) but
the expectancy is still negative — the literal direction is a
mean-reversion entry (buy after price has fallen, since P=10 sits
above P=30 in downtrends), so it wins often on small bounces and
loses big when the move continues into the 2xATR stop. It loses
less than the shipped direction on this window, but that is a
7-month in-sample observation on two losing systems, not a reason
to ship a directionally inverted crossover: the sine-wave phase
test proves the literal direction buys tops. Do not flip the
direction because of this table.

## One-line verdict

- **7/21:** the least bad combined (-$8,010) and the only green
  coin anywhere (HYPE +$803, PF 1.05) — but still negative on
  BTC/ETH and negative combined.
- **10/30 (shipped):** -$16,257; the a-priori pair from the brief.
- **14/42:** the worst (-$21,031, 3,045 trades) — longer periods
  cross MORE often under this alpha, not less, because the
  longer-period line tracks price ever more closely.
- **Shipped decision:** keep the specified 10/30 periods as the
  registry config regardless. No period pair turns this positive,
  and leaning toward 7/21 *because* it loses least would be
  in-sample selection on a losing system. The honest read: the
  crossover rate (~1 cross per 7 bars at 10/30) is the problem, and
  no period pair in this family fixes it on 1h crypto.
