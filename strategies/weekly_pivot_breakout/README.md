# Prior-Week Range Breakout

Classic weekly pivot breakout: the prior complete UTC week's
high/low is the range; a close outside it is a breakout, a close
back inside it ends the trade.

## Rules

- **Week:** UTC week starting Monday 00:00 UTC (Monday 00:00 to
  Sunday 23:00 UTC).
- **Levels:** prior-week high = highest high of the previous
  complete UTC week; prior-week low = lowest low of the same
  week. A week counts as complete only if all 168 hourly bars
  are present in the data.
- **Level updates:** only at week boundaries (the Monday 00:00
  UTC bar). The level in force on bar i is the last completed
  week's range, never an intraweek partial range.
- **Long entry:** close above the prior-week high.
- **Short entry:** close below the prior-week low.
- **Long exit:** close back below the prior-week high (back
  inside the range).
- **Short exit:** close back above the prior-week low.
- An opposite breakout is itself a close back inside the range
  for the other side, so it exits the open trade.
- Only one position at a time (harness rule).
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 200 bars (~1 week before the first signal is possible).

All computation is causal: the level on bar i comes only from
bars of weeks that ended before bar i's week started.

## Sources

- Prior-week high/low breakout (classic weekly pivot range):
  https://www.investopedia.com/terms/b/breakout.asp

## Files

- `indicators.py` — prior-week high/low levels + ATR(14)
- `signals.py` — entry/exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_weekly_pivot_breakout.py` — 18 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices + sweep

## How to run

From the repo root:

```
python3 -m pytest strategies/weekly_pivot_breakout/test_weekly_pivot_breakout.py -q
python3 strategies/weekly_pivot_breakout/run_backtest.py
```

## Verdict

LOSER on the shipped window: -$16,031.58 on 704 trades
(combined Sharpe -6.28, MaxDD -54.5%). Weekly-range breakouts
on hourly bars are mostly false breakouts in this window — 18.3%
win rate, profit factor 0.43. See BACKTEST.md.

Paper only, no live execution.
