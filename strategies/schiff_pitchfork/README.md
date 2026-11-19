# Schiff Pitchfork Median-Line Pullback

A Schiff pitchfork is a variant of the Andrews pitchfork. Both
are drawn from three consecutive pivots A, B, C, but the median
line differs: the standard Andrews fork anchors its median line
at A itself, while the Schiff fork anchors its median line at the
midpoint of A and B — (bar of A, (A + B) / 2) — and runs it
through the midpoint of B and C. The parallels pass through B and
C and share the median line's slope. That shifted anchor is the
whole point of the Schiff variant: it makes the fork flatter and
the median line sit closer to price, so pullbacks to the median
line happen sooner and more often than with a standard Andrews
fork. This strategy is distinct from the existing
`andrews_pitchfork` (standard anchor at A); the Schiff anchor at
(A+B)/2 is the difference.

## Rules

- **Pivots:** confirmed 10-bar pivots — a swing high at centre j
  iff h[j] is the max of the 10 bars h[j-7..j+2], a swing low iff
  l[j] is the min of l[j-7..j+2]; recorded at the confirmation bar
  (centre+2). Three consecutive pivots form a set: low-high-low
  (bullish) or high-low-high (bearish).
- **Long entry (bullish set):** price touches the median line from
  above — the bar's low within 0.5 ATR(14) of the median-line
  value — and then closes back above the median line. The touch
  bar itself counts if it closes back above; otherwise the touch
  arms the setup for the next 5 bars.
- **Short entry (bearish set):** the mirror — touch from below,
  close back below.
- **Long exit:** an opposite short signal OR a close below the
  lower parallel (the parallel through C).
- **Short exit:** an opposite long signal OR a close above the
  upper parallel (the parallel through C).
- Only the most recent set per side is active; a set expires 200
  bars after its C pivot confirms; a newly completed triple of the
  same side re-anchors.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

All computation is causal, so signals on bar i use only data
through bar i's close.

## Files

- `indicators.py` — 10-bar pivots, Schiff geometry, touch/arm
  state machines.
- `signals.py` — entry/exit booleans.
- `risk.py` — batch-standard risk config, WARMUP = 60.
- `run_backtest.py` — local-cache backtest runner.
- `test_schiff_pitchfork.py` — 16 unit tests, synthetic data only.

## How to run

From the repo root:

    python3 -m unittest strategies.schiff_pitchfork.test_schiff_pitchfork -v
    python3 strategies/schiff_pitchfork/run_backtest.py

## Sources

- FX Foundations, "Median Line / Pitchfork":
  https://www.fxfoundations.com/learn/technical-analysis/median-line-pitchfork

Paper only, no live execution.
