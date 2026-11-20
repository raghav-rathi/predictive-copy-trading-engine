# Adaptive MACD

MACD (Gerald Appel) with Kaufman efficiency-ratio adaptive EMAs:
the EMA smoothing constant speeds up in trending markets (ER near
1) and slows down in chop (ER near 0), so the MACD line adapts to
the regime instead of using fixed 12/26 periods.

## Rules

- **Efficiency ratio (10 bars):** ER = |close - close[10]| /
  sum(|close diffs| over 10 bars); ER = 0 on a flat stretch.
- **Fast adaptive EMA:** SC_fast = (ER*(2/3 - 2/13) + 2/13)^2
  (period range 2..12), recursion EMA[i] = EMA[i-1] +
  SC[i]*(close[i] - EMA[i-1]), seeded with close[10].
- **Slow adaptive EMA:** SC_slow = (ER*(2/6 - 2/27) + 2/27)^2
  (period range 5..26), same recursion and seeding.
- **MACD line:** fast adaptive EMA - slow adaptive EMA.
- **Signal line:** 9-bar EMA of the MACD line, seeded with the
  first MACD value.
- **Long entry:** MACD crosses above signal.
- **Short entry:** MACD crosses below signal.
- **Long exit:** opposite cross (MACD below signal).
- **Short exit:** opposite cross (MACD above signal).
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

All computation is causal: ER uses closes through bar i, and both
EMA recursions step forward one bar at a time.

## Sources

- Perry Kaufman, "Trading Systems and Methods" (efficiency ratio /
  KAMA adaptive smoothing).
- Gerald Appel, MACD:
  https://en.wikipedia.org/wiki/MACD

## Files

- `indicators.py` — ER, adaptive smoothing constants, adaptive EMAs, MACD/signal
- `signals.py` — cross entry/exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_adaptive_macd.py` — 19 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices

## How to run

From the repo root:

```
python3 -m pytest strategies/adaptive_macd/test_adaptive_macd.py -q
python3 strategies/adaptive_macd/run_backtest.py
```

## Verdict

Loser: -$5,587.65 combined on 998 trades (PF 0.87, Sharpe -1.31).
BTC and ETH both lose; only HYPE is nominally green. See BACKTEST.md.

Paper only, no live execution.
