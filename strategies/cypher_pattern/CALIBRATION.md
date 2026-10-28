# Cypher Harmonic Pattern — Calibration

## Parameter choices

| Parameter | Value | Why |
|---|---|---|
| Pivot confirmation | 5 bars each side | Matches the ABCD precedent in this repo; a pivot is only usable once its window is fully known, which is what makes the detector causal. |
| Window | 60 bars X..D | Carney-style patterns must complete in a bounded span or they are not one pattern; 60 bars (~2.5 days at 1h) keeps legs related. |
| AB/XA | 38.2–61.8% ± 8pp → 30.2–69.8% | Carney's band, with an explicit tolerance so near-miss geometry is not discarded by tick-level noise. |
| BC/AB | 113–141.4% ± 8pp → 105–149.4% | The Cypher's defining extension past A. |
| CD/XC | 78.6% ± 8pp → 70.6–86.6% | The completion level. |
| Stop / trail | 2.0x / 2.5x ATR | Batch standard; roomy enough for a reversal leg. |
| Max hold | 168 bars (~7 days) | A D pivot that has not turned in a week was not a turn. |
| Risk / leverage | 1% / 3x | Batch standard. |

## Sensitivity note

The ±8pp tolerance is doing real work here: without any
tolerance, textbook harmonic bands almost never complete on noisy
1h pivots. Widening it further would manufacture trades by
relabeling ordinary zigzags as Cyphers — that was explicitly not
done, and the 8-trade count is the honest consequence. Narrowing
it would likely leave zero trades. Either way, the sensitivity
runs in the direction of "this pattern does not occur often
enough at 1h to evaluate", not toward a hidden winner.

## Verdict: inconclusive

Ship as documented-inconclusive. The next honest step would be a
longer window or a shorter timeframe to get a real sample — not
tolerance tuning on this one.
