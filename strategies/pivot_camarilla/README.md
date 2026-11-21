# Camarilla Pivot Breakout

Nick Scott's Camarilla Equation (1989): daily pivot levels built
from the prior completed UTC day's high, low, and close. This
strategy trades the breakout — long when the close crosses above
R3, short when it crosses below S3 — and exits on a cross back
through the level.

## Rules

- **Levels (prior completed UTC day only):**
  R3 = C_prev + (H_prev - L_prev) * 1.055,
  S3 = C_prev - (H_prev - L_prev) * 1.055.
- **No levels before the first full day completes** — bars in the
  first UTC day have NaN levels and no signals.
- **Long entry:** close crosses above R3 (transition only).
- **Short entry:** close crosses below S3 (transition only).
- **Long exit:** close crosses back below R3.
- **Short exit:** close crosses back above S3.
- Crosses are judged against the current bar's level for both the
  current and previous close, so a level jump at a day boundary
  cannot fire a signal by itself.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 200 bars (levels first appear after one full UTC day = 24
  bars; 200 gives generous margin).

All computation is causal: a bar's levels come only from days that
completed before the bar's own day started, and the level for a day
is fixed for the whole day.

## Sources

- BabyPips, "Camarilla Pivot Points":
  https://www.babypips.com/forexpedia/camarilla-pivot
- Nick Scott, Camarilla Equation (1989).

Note: the assigned 1.055 factor differs from the canonical Camarilla
R3 factor of 1.1/4 = 0.275 — see CALIBRATION.md.

## Files

- `indicators.py` — prior-day Camarilla R3/S3, ATR(14)
- `signals.py` — R3/S3 cross entry/exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_pivot_camarilla.py` — 15 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices

## How to run

From the repo root:

```
python3 -m pytest strategies/pivot_camarilla/test_pivot_camarilla.py -q
python3 strategies/pivot_camarilla/run_backtest.py
```

## Verdict

Loser: -$1,523.04 combined on 250 trades (PF 0.84, Sharpe -0.82).
Only HYPE is green (+$672.64); BTC and ETH lose, win rate 24.0%.
Breakouts of a level a full prior-day range away mostly fail and
come straight back — see BACKTEST.md.

Paper only, no live execution.
