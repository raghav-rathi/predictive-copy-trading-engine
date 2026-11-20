# Prior-Week Range Breakout — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a
priori from the spec, and the backtest numbers were reported as-is.
A small two-alternate sweep was run after the fact and is reported
honestly below; the shipped config was NOT changed on its basis.

| Parameter | Value | A priori rationale |
|---|---|---|
| Week definition | UTC week, Monday 00:00 UTC to Sunday 23:00 UTC | The spec: the week starts Monday 00:00 UTC. |
| Prior-week high/low | highest high / lowest low of the previous complete UTC week | The spec: the range of the last completed week. |
| Completeness | a week counts only if all 168 hourly bars are present | The spec's "complete" week; the first partial week at the start of the data yields NaN levels, so no signal fires before the first full week is observed. |
| Level updates | only at week boundaries (Monday 00:00 UTC bar) | The spec: the level in force is the last completed week's range, never an intraweek partial range. |
| Entry | close above prior-week high (long) / below prior-week low (short) | The spec: the close, not the wick, breaks the level. |
| Exit | close back inside the range (below the high for longs / above the low for shorts) | The spec: a close back inside ends the trade; an opposite breakout is itself a close back inside for the other side. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 200 | ~1 week of bars before the first signal is possible; 200 bars clears the first completed week. |

## Sweep (2 alternates, run after the shipped backtest)

Combined across BTC/ETH/HYPE, same window and risk layer:

| Config | Trades | Win% | Net $ | Profit factor | Fees $ |
|---|---|---|---|---|---|
| **Shipped span=1, wicks** | **704** | **18.3%** | **-16031.58** | **0.43** | **3346.22** |
| Alt span=2, wicks | 509 | 17.7% | -12477.46 | 0.45 | 2631.74 |
| Alt span=1, closes-only | 842 | 18.2% | -18253.11 | 0.42 | 3954.77 |

A two-week range fires less often and loses less in dollars
(-$12,477) but the win rate and profit factor are no better
(17.7%, 0.45) — it is the same losing structure with fewer
trades, not an edge. Closes-only levels fire more often and lose
more. Neither alternate was adopted.

## Spec decisions / ambiguities

1. **The first week in the data is partial.** The window starts
   Saturday 2026-03-14 22:00 UTC, so the Mar 9 week is only
   ~26 bars in the cache and is NOT treated as complete. The
   first levels appear at bar 194 (Monday Mar 23 00:00 UTC),
   once the Mar 16–22 week has fully completed — verified by
   unit test.
2. **Levels are wick-based** (weekly high/low), while the entry
   is close-based. A wick through the level without a close
   beyond it does not enter.
3. **Entry and exit are level-based, not edge-based.** Every bar
   closing outside the range is an entry signal and every bar
   closing inside is an exit signal; the harness acts on the
   first entry and the first exit while in a position.
4. **An opposite breakout exits the open trade.** A close below
   the prior-week low is also below the prior-week high, so it
   satisfies the long-exit condition; no separate opposite-signal
   rule is needed.
5. **Span>1 (sweep only):** the range spans the last WEEK_SPAN
   complete weeks, taking the max high / min low across them; a
   span week that is incomplete in the data is skipped rather
   than invalidating the level. Shipped span is 1, where this
   cannot arise.

## What the exits actually did

Shipped run (704 trades): 455 trades ended on the harness stop /
trail and 249 on the signal exit (close back inside the range).
The stop-heavy mix is the false-breakout story: price breaks the
level, the stop is 2xATR away, and the reversal usually reaches
the stop before the close comes back inside.

No bug fixes requiring re-runs, no PnL-selected tuning.
