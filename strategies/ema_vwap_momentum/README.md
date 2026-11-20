# EMA Cross + Session VWAP Momentum

A classic EMA crossover filtered by the session VWAP: trade the
cross only when price is already on the right side of the day's
volume-weighted average price, and exit as soon as price gives
back that side of VWAP or the EMAs cross back.

## Rules

- **EMA(9) / EMA(21):** exponential moving averages of the close.
- **Session VWAP:** anchored to each UTC day (reset 00:00 UTC),
  VWAP = cumulative sum(tp × v) / sum(v), tp = (h + l + c) / 3.
- **Long entry:** EMA(9) crosses above EMA(21) while the close is
  above the session VWAP.
- **Short entry:** EMA(9) crosses below EMA(21) while the close is
  below the session VWAP.
- **Long exit:** EMA cross against OR the close crosses back below
  the session VWAP.
- **Short exit:** EMA cross against OR the close crosses back above
  the session VWAP.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

All computation is causal: the VWAP uses only bars of the current
UTC day through bar i's close, and every signal on bar i uses data
through bar i's close.

## Sources

- Investopedia, "Volume-Weighted Average Price (VWAP)":
  https://www.investopedia.com/terms/v/vwap.asp

## Files

- `indicators.py` — EMA(9/21) + session VWAP (via `strategies.base`)
- `signals.py` — cross + VWAP-side entries, cross/VWAP exits
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_ema_vwap_momentum.py` — 21 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices + sweep

## How to run

From the repo root:

```
python3 -m pytest strategies/ema_vwap_momentum/test_ema_vwap_momentum.py -q
python3 strategies/ema_vwap_momentum/run_backtest.py
```

Paper only, no live execution.
