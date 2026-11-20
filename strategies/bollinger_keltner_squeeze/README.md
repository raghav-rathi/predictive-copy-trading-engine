# Bollinger/Keltner Squeeze

John Carter's TTM Squeeze: volatility compresses (Bollinger Bands
inside Keltner Channels) and then expands. This strategy trades the
expansion — the first bar the squeeze turns off — in the direction
of the TTM momentum histogram.

## Rules

- **Bollinger Bands:** SMA(20) ± 2.0 std.
- **Keltner Channels:** EMA(20) ± 1.5 x ATR(14).
- **Squeeze ON:** bb_upper < kc_upper AND bb_lower > kc_lower.
- **Momentum:** x = close - ((20-bar high-low midpoint + SMA(20)) / 2);
  momentum = fitted value at bar i of the 20-bar linear regression
  of x (mean + slope x 9.5).
- **Fire:** the first bar the squeeze turns OFF after being ON.
- **Long entry:** fire with momentum > 0.
- **Short entry:** fire with momentum < 0.
- **Long exit:** opposite (short) signal.
- **Short exit:** opposite (long) signal.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 40 bars (momentum is first defined at bar 38).

All computation is causal: rolling windows are trailing, the
regression is fit on the trailing 20 values of x, and the squeeze
state uses bars through the current close only.

## Sources

- PatternsWizard, "TTM Squeeze Indicator":
  https://patternswizard.com/ttm-squeeze-indicator/
- TrendSpider, "Introduction to TTM Squeeze":
  https://trendspider.com/learning-center/introduction-to-ttm-squeeze/

## Files

- `indicators.py` — Bollinger/Keltner bands, squeeze state, TTM momentum
- `signals.py` — fire entry/exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_bollinger_keltner_squeeze.py` — 18 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices

## How to run

From the repo root:

```
python3 -m pytest strategies/bollinger_keltner_squeeze/test_bollinger_keltner_squeeze.py -q
python3 strategies/bollinger_keltner_squeeze/run_backtest.py
```

## Verdict

Nominal winner, thin: +$366.04 combined on 379 trades (PF 1.02,
Sharpe 0.20). Only ETH is green; 360 of 379 exits are harness
stops, not signal exits. No robust edge — see BACKTEST.md.

Paper only, no live execution.
