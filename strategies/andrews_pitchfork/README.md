# Andrews Pitchfork

Andrews Pitchfork median-line system (Dr. Alan Andrews) on 5-bar fractal pivots. Take the most recent alternating pivot triple P0 (low), P1 (high), P2 (low) with P2 > P0; the median line runs from P0 through the midpoint of P1–P2, extended forward; the lower parallel runs through P2 and the upper parallel through P1, both parallel to the median line. The bearish fork is the mirror image (P0 high, P1 low, P2 high with P2 < P0; upper parallel through P2, lower through P1). The fork is recomputed whenever a newer completed pivot triple forms.

## Rules

- Long: the low comes within 0.25x ATR(14) of the bullish fork's lower parallel and the bar closes back above it (bounce). Target is the median line — exit long at a close reaching the median line.
- Short: the high comes within 0.25x ATR(14) of the bearish fork's upper parallel and the bar closes back below it. Target is the median line.
- Also exit on a close outside the fork, beyond the opposite parallel.
- A bounce counts once: consecutive bars meeting the same bounce condition do not re-fire.
- Pivots are 5-bar local extrema with a minimum 0.9x ATR(14) swing, usable only 2 bars after the extreme bar — no lookahead.

## Source

- Andrews Pitchfork median-line system (FX Foundations): https://www.fxfoundations.com/learn/technical-analysis/median-line-pitchfork

Paper only, no live execution.
