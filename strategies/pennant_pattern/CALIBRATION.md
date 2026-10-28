# Pennant Pattern — Calibration

## Parameter choices

| Parameter | Value | Why |
|---|---|---|
| Pole length / size | 5 bars, >= 3x ATR(14) | A pole must be sharp relative to recent volatility; 3x ATR over 5 bars is a genuine impulse, not drift. Shorter windows admit noise, longer ones admit whole trends. |
| Pole completion | Last bar stalled (<= 0.5x ATR move) | Mirrors the flag precedent in this repo: without a stall requirement, a steady trend triggers mid-pole and the "consolidation" is just the trend continuing. |
| Consolidation | 5–15 bars | Textbook pennants are brief; longer than 15 bars and the pattern is a range, not a pennant. |
| Convergence test | 3-bar blocks, highs falling + lows rising | Operationalizes "converging range" without fitting trendlines; 3 bars per side is the smallest block that is not a single-bar fluke. |
| Volume filter | > 1.2x prior 20-bar average | Breakouts without participation are the classic false-breakout signature; the average excludes the current bar so the breakout bar cannot inflate its own benchmark. |
| Armed expiry / invalidation | 15 bars / 0.5x ATR far-side break | A setup that has not broken out in 15 bars is stale; a far-side break means the range resolved the wrong way. |
| Stop / trail | 2.0x / 2.5x ATR | Batch standard; room past the range for a breakout to breathe. |
| Max hold | 168 bars (~7 days) | A breakout that has not paid in a week is not paying. |
| Risk / leverage | 1% / 3x | Batch standard. |

## Sensitivity note

The two filters that most shape the sample are the stall
requirement and the volume filter: dropping either would roughly
double trade count but admit exactly the low-quality setups both
exist to exclude (mid-trend poles, participation-free breakouts).
That trade was not tested by re-running variants — it is a design
judgment, and the shipped 24-trade sample is the price of it.
The verdict does not hinge on a threshold: at 24 trades, no
threshold tweak produces a credible winner, only a different
small sample.

## Verdict: flat-to-loser, thin sample

Ship as documented. A longer window is the only honest way to get
a real verdict on this detector; do not loosen the pole, volume,
or convergence rules on this data to chase trades.
