# Gaussian Filter Trend — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-10-18 13:00 UTC
(ms `[1773525600000, 1792328400000)`; actual data starts 2026-03-14
22:00 UTC for BTC/ETH, 2026-03-15 00:00 UTC for HYPE): 5,223 bars
BTC/ETH, 5,221 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=100 bars.

## Results (shipped config: 4-pole Gaussian filters of close, periods
10 and 30, alpha = (1−sin(2π/period))/cos(2π/period); CORRECTED
direction — long when the period-30 filter crosses above the
period-10 filter, short on a cross below; exits on the opposite
cross; 2xATR stop, 3xATR trail, 200-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 728 | 25.1% | -$7,424 | -74.3% | -6.76 | -75.8% | -$10.20 | 0.57 |
| ETH | 729 | 26.6% | -$5,049 | -50.6% | -3.23 | -58.6% | -$6.93 | 0.74 |
| HYPE | 696 | 29.7% | -$3,783 | -38.0% | -2.31 | -38.9% | -$5.44 | 0.81 |
| **Combined** | **2,153** | **27.1%** | **-$16,257** | — | — | — | **-$7.55** | — |

Entry gates all fire on every coin (long entries 357–374, short
entries 357–373 per coin).

## Verdict: a heavy loser, and a whipsaw machine

Combined -$16,257 across 2,153 trades — the worst trade count of
any strategy in this batch family and a win rate of just 27.1%. BTC
-$7,424 (PF 0.57, Sharpe -6.76, MaxDD -75.8%), ETH -$5,049 (PF
0.74), HYPE -$3,783 (PF 0.81). The two filters cross about every 7
bars on 1h crypto: the P=30 tracker hugs price (0.94-bar lag) while
the P=10 baseline lags 3.85 bars, so every wiggle in price flips
their order and fires an entry. Each flip pays the 0.045% + 0.01%
round-trip cost, and the 2xATR stop eats the rest — fees alone are
$12,012, nearly three-quarters of the total loss, and the
expectancy is negative before costs too (PF < 1 on every coin).

The honest read is that a Gaussian-filter crossover at these
periods is a chop amplifier on 1h crypto, not a trend filter: the
smoothing is real (both lines are smoother than price), but the
crossing rate is far too high for the signal to mean anything at
this timescale. Longer period pairs (CALIBRATION.md) cross even
more often and lose more.

## Mechanism

4-pole recursive Gaussian filters of close at periods 10 and 30
(Ehlers, Rocket Science for Traders Ch. 15). CORRECTED direction:
because Ehlers' alpha increases with period, the period-30 filter
is the fast tracker and period-10 the slow baseline — long when
the period-30 line crosses above the period-10 line, short on a
cross below, exits on the opposite cross. 2xATR hard stop, 3xATR
chandelier trail, 200-bar max hold. See README.md / CALIBRATION.md
for the verification.

Sources: Gaussian Filter (Ehlers) —
https://www.luxalgo.com/library/indicator/gaussian-filter/ and
http://www2.wealth-lab.com/WL5wiki/Print.aspx?Page=Gaussian

## Limitations

- Single 7-month crypto window; 2,153 trades is a large sample and
  all three legs agree — this does not work on 1h crypto in this
  regime, in either crossover direction (the literal inverted
  direction also loses, -$14,853 combined; see CALIBRATION.md).
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped periods on this window (see
  CALIBRATION.md — no period pair turns this positive).
