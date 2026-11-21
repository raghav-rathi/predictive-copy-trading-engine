# MACD Histogram Divergence

Gerald Appel's MACD(12, 26, 9) divergence: when price makes a new
swing low but the MACD histogram does not, momentum is fading and
a turn may be near. This strategy trades divergences on confirmed
swing pivots only — a pivot is confirmed 2 bars after the extreme,
so the signal is causal — and exits on the opposite divergence or
a histogram zero-line cross.

## Rules

- **MACD** = EMA(12) − EMA(26); **signal** = EMA(9) of MACD;
  **hist** = MACD − signal.
- **Swing low:** bar i is a swing low if l[i] is the minimum of
  l[i−2..i+2] and strictly below l[i−1]; confirmed at bar i+2.
  Swing high is the mirror on h.
- **Bullish divergence:** a confirmed swing low LOWER than the
  previous confirmed swing low within the last 60 bars, while hist
  at that low is HIGHER than hist at the previous swing low, AND
  hist turns up (hist[j] > hist[j−1]) on the confirmation bar j.
- **Bearish divergence:** mirror (higher swing high, lower hist,
  hist turns down on the confirmation bar).
- **Long entry:** bullish divergence confirmation.
- **Short entry:** bearish divergence confirmation.
- **Long exit:** bearish divergence confirmation OR hist crosses
  below 0.
- **Short exit:** bullish divergence confirmation OR hist crosses
  above 0.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 80 bars (MACD first defined ~bar 33; a divergence needs
  two pivots up to 60 bars apart plus confirmation).

All computation is causal: pivots are evaluated only on their
confirmation bar, using data through that bar only.

## Sources

- Gerald Appel, MACD (Moving Average Convergence Divergence),
  late 1970s; MACD(12, 26, 9) reference:
  https://en.wikipedia.org/wiki/MACD

## Files

- `indicators.py` — MACD(12, 26, 9), confirmed swing pivots, divergences
- `signals.py` — divergence entry/exit and zero-cross exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_macd_histogram_divergence.py` — 17 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices

## How to run

From the repo root:

```
python3 -m pytest strategies/macd_histogram_divergence/test_macd_histogram_divergence.py -q
python3 strategies/macd_histogram_divergence/run_backtest.py
```

## Verdict

Loser, thin: −$2,214.41 combined on 475 trades (PF 0.90,
Sharpe −0.73). Only HYPE is green (+$1,011.70); BTC carries the
loss (−$2,627.61) and 318 of 475 exits are harness stops. No
robust edge — see BACKTEST.md.

Paper only, no live execution.
