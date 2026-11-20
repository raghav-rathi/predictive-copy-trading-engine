# Stochastic %K/%D Cross + MACD Histogram

George Lane's stochastic oscillator crossed with Gerald Appel's
MACD: enter only when the fast oscillator turns out of an extreme
zone AND the MACD histogram agrees with the direction.

## Rules

- **Stochastic(14,3,3):** raw %K = 100 * (close - lowest low of
  14) / (highest high of 14 - lowest low of 14); %K = SMA(3) of
  raw %K; %D = SMA(3) of %K.
- **MACD(12,26,9):** line = EMA(12) - EMA(26); signal = EMA(9)
  of the line; histogram = line - signal.
- **Long entry:** %K crosses above %D while %K < 30 AND the MACD
  histogram is > 0 — all three on the same bar.
- **Short entry:** %K crosses below %D while %K > 70 AND the
  MACD histogram is < 0 — all three on the same bar.
- **Long exit:** %K crosses below %D OR the histogram flips
  negative.
- **Short exit:** %K crosses above %D OR the histogram flips
  positive.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 40 bars.

All computation is causal: every value on bar i uses data through
bar i's close only. The cross compares bar i with bar i-1.

## Sources

- George Lane, stochastic oscillator:
  https://www.investopedia.com/terms/s/stochasticoscillator.asp
- Gerald Appel, MACD:
  https://www.investopedia.com/terms/m/macd.asp

## Files

- `indicators.py` — Stochastic(14,3,3) + MACD(12,26,9) + ATR(14)
- `signals.py` — entry/exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_stochastic_macd.py` — 19 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices + sweep

## How to run

From the repo root:

```
python3 -m pytest strategies/stochastic_macd/test_stochastic_macd.py -q
python3 strategies/stochastic_macd/run_backtest.py
```

## Verdict

LOSER on the shipped window: -$1,258.04 on 97 trades (combined
Sharpe -2.01, MaxDD -4.4%). The dual-confirmation gate fires
rarely and the signals it takes lose on all three coins. See
BACKTEST.md.

Paper only, no live execution.
