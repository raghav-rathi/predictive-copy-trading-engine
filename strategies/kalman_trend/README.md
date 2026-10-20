# Kalman Filter Trend

Trend-following on a 1-D Kalman filter with a price+velocity state
estimated on hourly closes. The velocity state lets the filter track a
sustained drift with almost no steady-state lag, while the measurement
noise term damps one-bar spikes.

- **Long:** close crosses above the filter estimate `kf` AND the filter
  is already rising (`kf_slope > 0`)
- **Short:** close crosses below `kf` AND the filter is already falling
  (`kf_slope < 0`)
- **Exits:** the bare opposite cross (no slope condition) — once the
  close crosses back through the filter, the premise is dead
- **Risk:** 2xATR hard stop, 200-bar max hold, 1% risk/trade, 3x leverage

The slope confirmation exists to filter out flat-chop taps where the
filter is stationary — a cross alone whipsaws on every touch.

## Parameters

- `Q = diag(0.05, 0.01)` — process noise (price jitter, velocity drift)
- `R = 1.0` — measurement noise (the smoothing knob; see CALIBRATION.md)
- Slope confirmation required on entries, not on exits
- Stop: 2xATR(14); no trailing, no fixed target
- Max hold: 200 bars; WARMUP = 40 bars
- Sizing: 1% equity risk per trade, 3x leverage cap

## Usage

```python
from strategies.kalman_trend import indicators, signals, risk

sig_df = signals.add_signals(indicators.add_indicators(df))  # df: t,o,h,l,c,v
# or with a different measurement noise for research only:
# sig_df = signals.add_signals(indicators.add_indicators(df, r=2.0))
from strategies.backtest import run_backtest
res = run_backtest(sig_df, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                   use_funding=False)
```

See BACKTEST.md for the 2026-03-14 → 2026-10-20 Hyperliquid 1h
(BTC/ETH/HYPE) results and CALIBRATION.md for the measurement-noise
(r = 0.5 / 1.0 / 2.0) sensitivity check.
