# Gaussian Filter Trend

Trend-following crossover on John Ehlers' 4-pole recursive Gaussian
filter — "Rocket Science for Traders" Ch. 15.

- **alpha** = (1 − sin(2π/period)) / cos(2π/period)
- **4-pole recursion:** f = α⁴·g + 4(1−α)·f[1] − 6(1−α)²·f[2]
  + 4(1−α)³·f[3] − (1−α)⁴·f[4], applied to close
- **Two filters:** period 10 and period 30
- **Long:** the period-30 filter crosses above the period-10 filter
- **Short:** the period-30 filter crosses below the period-10 filter
- **Exit:** the opposite cross
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 200-bar max hold
  (trend legs need room), 1% risk/trade, 3x leverage

## The correction — read this before using the strategy

The crossover direction is the OPPOSITE of the naive "fast 10 /
slow 30" reading, and this is verified, not assumed. With Ehlers'
alpha formula, alpha INCREASES with period (0.5095 at P=10, 0.8098
at P=30), so the per-stage pole b = 1−α is smaller for the longer
period and the group delay 4b/(1−b) is 3.85 bars for P=10 but only
0.94 bars for P=30. Measured: on a rising ramp the P=30 line sits
0.094 below price while the P=10 line sits 0.385 below it; on a
sine wave the P=10 line crosses above the P=30 line at price TOPS
and below it at price BOTTOMS. The formula and the recursion are
Ehlers' published forms (the recursion matches the published 4-pole
expansion exactly; the alpha form matches the (1−sin θ)/cos θ form
used in this repo's ehlers_sinewave) — what is corrected is the
ROLE assignment: the period-30 filter is the fast tracker, the
period-10 filter the slow baseline. Shipping the literal "P=10
crosses above P=30 = long" would buy tops and sell bottoms. Columns
are therefore named by period (`gf_p10`, `gf_p30`) with no
fast/slow labels. Full verification numbers in CALIBRATION.md.

Parameters: periods 10 and 30, 4 poles, ATR(14) for stop/trail.
WARMUP=100 (the slow baseline's lag is ~4 bars; 100 is margin).

Usage:

```python
from strategies.data import fetch_candles
from strategies.gaussian_filter_trend import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))  # 10/30 defaults
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the period-pair sensitivity check and the full
alpha verification.

Sources: Gaussian Filter (John Ehlers, Rocket Science for Traders
Ch. 15) — https://www.luxalgo.com/library/indicator/gaussian-filter/
and http://www2.wealth-lab.com/WL5wiki/Print.aspx?Page=Gaussian

## Honest caveats

- The backtest on this window is a heavy loser on all three coins
  (combined -$16,257, PF 0.57–0.81) — see BACKTEST.md. The two
  filters cross ~every 7 bars on 1h crypto, so this is a whipsaw
  machine in chop: 2,153 trades in 7 months, 27.1% win rate, fees
  alone $12,012.
- The correction is justified by filter mathematics (sine-wave
  phase test), NOT by backtest PnL: the literal (inverted)
  direction also loses on this window (-$14,853 combined), just
  slightly less. Neither direction works here; the shipped one is
  the directionally correct crossover.
- The Wealth-Lab "critical period attenuated by 50%" claim does not
  hold exactly for the 4-pole cascade with this alpha: a 30-bar
  cycle passes the P=30 filter at ~97.5% amplitude. Treat "period"
  as a tuning label, not a precise cutoff.
