# Vortex + ADX — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Vortex length | 14 | Botes & Siepman's standard setting; the most common published default. |
| VM+ | \|high - previous low\| | Botes & Siepman's positive vortex movement, verbatim. |
| VM- | \|low - previous high\| | Mirror of VM+. |
| TR | Wilder true range | Shared `strategies.base.true_range` primitive. |
| VI smoothing | EMA(14) ratios: VI+ = EMA(VM+, 14) / EMA(TR, 14) | Per the batch spec. See deviation note below — the published formula uses 14-period sums, not EMAs. |
| ADX length | 14 | Wilder's standard ADX length; matches the Vortex length. |
| ADX entry threshold | > 25 | Standard "strong trend" threshold; the spec's value. |
| ADX exit threshold | < 20 | Standard "trend fading" threshold; the spec's value. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 30 | EMA(14) + ADX(14) spin-up (ADX first finite ~bar 27), with margin. |

## Spec deviations

1. **EMA(14) ratios instead of the published 14-period sums.**
   Botes & Siepman define VI+ = sum(VM+, 14) / sum(TR, 14) — equal
   weights over a rolling 14-bar window. The batch spec prescribes
   EMA(14) ratios instead, and the shipped build follows the spec.
   The EMA version weights recent bars more heavily, so the lines
   react faster and cross slightly more often than the published
   version; the cross logic itself is unchanged. The published
   sum-based variant was not built or tested.
2. **ADX filter added to the published indicator.** Botes &
   Siepman's article presents the VI cross as a standalone signal.
   The ADX > 25 entry filter and ADX < 20 exit are the spec's
   addition (the standard remedy for the Vortex's known sideways-
   market weakness) and were fixed before seeing results.
3. **Harness stop/trail as the practical exit.** The batch-standard
   risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold) is
   applied on top of the signal exit, per the spec's own
   instruction. 596 of 884 trades still end on the signal exit, so
   the signal exit — not the stop — is what mostly drives this
   result.

No bug fixes requiring re-runs, no PnL-selected tuning.
