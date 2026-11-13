# ATR Trailing Stop — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| ATR window | 14 | Wilder's ATR default and the batch-standard window; the task spec fixes ATR(14). |
| ATR multiplier | 3.0 | The canonical Chandelier multiplier (LeBeau's default, 3x ATR). |
| Anchor | Highest high / lowest low since the regime started | LeBeau's original formulation hangs the stop from the extreme since trade entry; the shipped anchor is the extreme since the regime started, which is the same thing for a system whose "trade" is the regime. |
| Ratchet | Stop only moves in the regime's favour | Canonical Chandelier behaviour: a rising ATR without a new extreme never loosens the stop. |
| Entry / exit | Regime flip on a close crossing the stop | Per spec: the close crossing the trailing stop is the flip, the entry, and the exit. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | ATR(14) needs 14 bars and the regime needs a few dozen bars to establish an anchor; 60 gives margin. |

## Spec deviations

1. **Anchor since regime start, not a fixed 22-bar window.** The
   charting-platform adaptation of the Chandelier Exit uses a fixed
   22-bar highest high / lowest low; LeBeau's original hangs the stop
   from the extreme since trade entry. The task spec fixes the anchor
   as "highest high since regime start", which matches LeBeau's
   original and is what ships.
2. **ATR(14) instead of ATR(22).** The 22-bar Chandelier variant
   pairs the 22-bar extreme with ATR(22). The task spec fixes
   ATR(14), and the batch-standard risk layer is also ATR(14), so
   ATR(14) ships.
3. **Seed regime.** The first bar with a valid ATR seeds a regime
   (long if its close is at or above its own stop, short otherwise).
   By the 60-bar warmup the seed regime has normally been replaced
   by a genuine flip.
4. **Harness stop/trail as the practical exit.** LeBeau's system
   exits on the stop cross alone. The batch-standard risk layer
   (2xATR stop, 2.5xATR trail, 120-bar max hold) is applied on top,
   per the spec's own instruction; because the 2xATR harness stop
   sits inside the 3xATR Chandelier stop, it fires first on almost
   every trade, so the regime flip is decorative as an exit in
   practice.

No bug fixes requiring re-runs, no PnL-selected tuning.
