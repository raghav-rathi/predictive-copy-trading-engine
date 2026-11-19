# Turn of the Month

Long-only calendar effect (Lakonishok & Smidt window): buy the
turn of the month, sell a few days into the new month.

## Rules

- **Long entry:** the first bar of the last calendar day of each
  month — the 00:00 UTC bar. The harness executes at the next
  bar's open, so the fill is the 01:00 UTC open of the last day.
- **Long exit:** the 23:00 UTC bar of the 3rd calendar day of
  the next month. The harness executes at the next bar's open,
  so the fill is the 00:00 UTC open of day 4.
- **No shorts:** `allow_shorts=False`; `short_entry` and
  `short_exit` are always False.
- Date logic uses ONLY the bar timestamp `t` (UTC) — never
  wall-clock time. `days_in_month` handles 28/29/30/31-day
  months (February 2026: 28 days, not a leap year).
- If a month's 00:00 bar (last day) or 23:00 bar (day 3) is
  missing from the data, that month simply produces no entry /
  no signal exit for that leg.
- The harness risk layer's 2xATR stop / 2.5xATR trail also
  applies. Max hold 120 bars covers the ~5-day window
  (~95–120 bars from fill to exit fill).
- Warmup 60 bars.
- Expect ~8 longs per coin over the window (month-ends Mar 31
  through Oct 31); selective is fine and honest — the window
  was NOT widened to manufacture trades.

## Sources

- Quantpedia, "Turn of the Month in Equity Indexes":
  https://quantpedia.com/strategies/turn-of-the-month-in-equity-indexes

## Files

- `indicators.py` — UTC calendar columns from the bar timestamp
- `signals.py` — long-only entry/exit
- `risk.py` — batch-standard risk config, long-only, warmup 60
- `test_turn_of_month.py` — 12 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` / `CALIBRATION.md` — results and parameter notes

## How to run

From the repo root:

```
python3 -m unittest strategies.turn_of_month.test_turn_of_month -v
python3 strategies/turn_of_month/run_backtest.py
```

Paper only, no live execution.
