# Livermore Pivotal Point

Jesse Livermore's pivotal-point / Market Key system (How to Trade
in Stocks, 1940): a market consolidates in a narrow range, breaks
out of the range on expanding volume (the pivotal point), reacts
back toward the pivot on contracting volume without violating it
(the natural reaction), and then resumes in the break direction.
The resumption close is the entry — Livermore traded the
resumption, not the breakout itself, because the reaction proves
the pivot holds as support/resistance.

## Rules

- **Consolidation:** a 20-bar window whose range (max high − min
  low) is < 0.6× the median 20-bar range of the prior 100 bars.
  The bull pivot is that window's high, the bear pivot its low;
  the pivot is frozen when the window completes. A newly
  completed consolidation replaces the active pivot.
- **Long entry (bullish):** close above the bull pivot with volume
  > 1.25× the 20-bar mean volume (the break); then within 10 bars
  a natural reaction — a bar whose close is below the break bar's
  close, whose low stays above the pivot, and whose volume is
  below the 20-bar mean; then a close above the reaction high
  (highest high from the break bar through the reaction bar) with
  volume above the 20-bar mean.
- **Short entry (bearish):** the mirror.
- **Long exit:** an opposite short signal OR a close back below
  the bull pivot (Livermore's danger signal).
- **Short exit:** an opposite long signal OR a close back above
  the bear pivot.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 120 bars (the range median needs 100 prior 20-bar
  windows).

All computation is causal, so signals on bar i use only data
through bar i's close.

## Files

- `indicators.py` — consolidation detection, pivot freezing, the
  break / reaction / resumption state machines.
- `signals.py` — entry/exit booleans.
- `risk.py` — batch-standard risk config, WARMUP = 120.
- `run_backtest.py` — local-cache backtest runner.
- `test_livermore_pivotal.py` — 18 unit tests, synthetic data only.

## How to run

From the repo root:

    python3 -m unittest strategies.livermore_pivotal.test_livermore_pivotal -v
    python3 strategies/livermore_pivotal/run_backtest.py

## Sources

- MQL5, "Jesse Livermore's Trading System":
  https://www.mql5.com/en/articles/24075
- Jesse Livermore, How to Trade in Stocks (1940).

Paper only, no live execution.
