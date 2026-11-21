# Connors RSI(2)

Larry Connors' Connors RSI (CRSI): a 0–100 composite of three
short-horizon mean-reversion components. This strategy trades its
extremes — long when CRSI crosses below 10, short when it crosses
above 90 — and exits when CRSI crosses back through 50.

## Rules

- **CRSI** = mean of:
  - RSI(3) of the close (Wilder),
  - RSI(3) of the up/down streak series (streak +1 on an up close,
    −1 on a down close, reset to 0 on an unchanged close),
  - percentile rank of the 1-bar ROC over the trailing 100 bars
    (100 × count of ROC values strictly below today's / 100).
- **Long entry:** CRSI crosses below 10 (transition only).
- **Short entry:** CRSI crosses above 90 (transition only).
- **Long exit:** CRSI crosses above 50.
- **Short exit:** CRSI crosses below 50.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 120 bars (the percentile rank needs 100 fully-defined
  ROC values; the first CRSI is at bar 100).

All computation is causal: trailing windows only, no lookahead.

## Sources

- Larry Connors & Cesar Alvarez, *Short Term Trading Strategies
  That Work* (2008); Connors RSI formula reference:
  https://therighttrader.com/learn/indicators/connors-rsi

## Files

- `indicators.py` — streak series, RSI(3) pair, ROC percentile rank, CRSI
- `signals.py` — 10/90 entry and 50 exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_rsi2_connors.py` — 16 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices

## How to run

From the repo root:

```
python3 -m pytest strategies/rsi2_connors/test_rsi2_connors.py -q
python3 strategies/rsi2_connors/run_backtest.py
```

## Verdict

Loser: −$4,722.13 combined on 452 trades (PF 0.61, Sharpe −3.73).
Win rate 58.0% but average losses dwarf average wins — buying
every sub-10 dip in a downtrend window catches falling knives.
See BACKTEST.md.

Paper only, no live execution.
