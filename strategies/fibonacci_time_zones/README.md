# Fibonacci Time Zones Pullback

Fibonacci time zones are vertical lines drawn at Fibonacci bar
counts after a swing anchor — here 8, 13, 21 and 34 bars after
the most recent confirmed swing high/low. Time zones alone give
timing, not direction: they mark the bars where a turn is
*likely*, not which way price will go. The direction in this
strategy comes from an EMA pullback confirmation inside the zone
window: the zone says *when* to look, the pullback says *which
way*.

## Rules

- **Anchor:** the most recent confirmed 10-bar swing high/low
  (swing high at centre j iff h[j] is the max of h[j-7..j+2], a
  swing low iff l[j] is the min of l[j-7..j+2]; recorded at the
  confirmation bar, centre+2). A newly confirmed swing
  re-anchors the zones.
- **Zone window:** a bar is in the zone if it is within ±1 bar of
  a zone count (anchor bar + 8 / 13 / 21 / 34).
- **Long entry:** the anchor was a swing LOW and the close is
  above EMA(50) (uptrend); a pullback — a close below EMA(20) at
  any point since the anchor — is followed by a close back above
  EMA(20), and that reclaim bar falls inside a zone window (and
  is a genuine cross: the previous bar's close was at or below
  its EMA(20)).
- **Short entry:** the mirror — anchor was a swing HIGH, close
  below EMA(50) (downtrend), a rally close above EMA(20) then a
  close back below EMA(20) inside a zone window.
- **If no confirmation lands inside the ±1-bar window, the zone
  passes with no trade.**
- **Long exit:** an opposite short signal OR a close below the
  most recent confirmed swing low (the anchor low).
- **Short exit:** an opposite long signal OR a close above the
  most recent confirmed swing high (the anchor high).
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

All computation is causal, so signals on bar i use only data
through bar i's close.

## Files

- `indicators.py` — 10-bar pivots, zone windows, EMA pullback
  tracking.
- `signals.py` — entry/exit booleans.
- `risk.py` — batch-standard risk config, WARMUP = 60.
- `run_backtest.py` — local-cache backtest runner.
- `test_fibonacci_time_zones.py` — 16 unit tests, synthetic data only.

## How to run

From the repo root:

    python3 -m unittest strategies.fibonacci_time_zones.test_fibonacci_time_zones -v
    python3 strategies/fibonacci_time_zones/run_backtest.py

## Sources

- The Right Trader, "Fibonacci Time Zones":
  https://therighttrader.com/learn/fibonacci-and-drawing-tools/fibonacci-time-zones

Paper only, no live execution.
