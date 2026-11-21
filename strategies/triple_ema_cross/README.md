# Triple EMA Crossover

Triple moving-average crossover: EMA(5) crossing EMA(13) is the
trigger, and the EMA(50) stack is the trend filter — trade only in
the direction the three EMAs are stacked.

## Rules

- **EMAs:** EMA(5) fast, EMA(13) mid, EMA(50) slow.
- **Long entry:** EMA(5) crosses up through EMA(13) AND
  EMA5 > EMA13 > EMA50 on that bar (transition only).
- **Short entry:** EMA(5) crosses down through EMA(13) AND
  EMA5 < EMA13 < EMA50 on that bar (transition only).
- **Long exit:** EMA(5) crosses down through EMA(13).
- **Short exit:** EMA(5) crosses up through EMA(13).
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 70 bars (slowest EMA needs 50 bars).

All computation is causal: every EMA value on bar i uses closes
through bar i only.

## Sources

- HowToTrade, "The Triple Moving Average Crossover Strategy (With
  Examples)":
  https://howtotrade.com/trading-strategies/triple-moving-average-crossover/

## Files

- `indicators.py` — EMA(5)/EMA(13)/EMA(50), ATR(14)
- `signals.py` — cross + stack entry / cross-back exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_triple_ema_cross.py` — 15 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices

## How to run

From the repo root:

```
python3 -m pytest strategies/triple_ema_cross/test_triple_ema_cross.py -q
python3 strategies/triple_ema_cross/run_backtest.py
```

## Verdict

Loser, worst of batch 42: -$5,244.33 combined on 539 trades
(PF 0.75, Sharpe -1.85, win rate 24.1%). All three coins lose; the
EMA cross whipsaws on 1h crypto. One calibration alternate (9/21/55)
was profitable but was NOT adopted — see CALIBRATION.md.

Paper only, no live execution.
