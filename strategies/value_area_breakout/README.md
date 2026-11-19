# Value-Area Breakout

Volume-profile value-area breakout: each UTC day's value area is
built from the prior completed day's volume profile, and a
two-close acceptance beyond it is the entry — one close outside
is a poke, two is acceptance.

## Rules

- **Profile (per UTC day):** from the prior completed day's 24
  bars, 50 price bins across [day low, day high]; each bar's
  volume goes to the bin containing its close. POC = the bin with
  max volume; expand outward from the POC, adding the heavier
  adjacent bin first, until cumulative volume >= 70% of the day's
  volume. VAH = top edge of the highest bin included, VAL = bottom
  edge of the lowest bin included. The profile is available from
  the 00:00 UTC bar of the new day and is recomputed every day.
- **Long entry:** the 2nd consecutive close above VAH.
- **Short entry:** the 2nd consecutive close below VAL.
- **Long exit:** a close back at or below VAH (rejection into the
  value area, or opposite acceptance below VAL).
- **Short exit:** a close back at or above VAL.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars (two full days are needed before the first
  profile exists; 60 gives margin).

The consecutive-close streak resets at each UTC day boundary (the
levels change) and whenever a close prints back inside the value
area. All computation is causal: a bar's profile, counts, and
triggers use only data through that bar's close.

## Sources

- Trading Strategy Guides, "Volume Profile Trading Strategy":
  https://tradingstrategyguides.com/volume-profile-trading-strategy/

## Files

- `indicators.py` — prior-day volume profile + acceptance counts
- `signals.py` — entry/exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_value_area_breakout.py` — 15 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices

## How to run

From the repo root:

```
python3 -m unittest strategies.value_area_breakout.test_value_area_breakout -v
python3 strategies/value_area_breakout/run_backtest.py
```

Paper only, no live execution.
