# Bill Williams Market Facilitation Index Squat Breakout — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| BW MFI | (high − low) / volume | Williams, "Trading Chaos" — the defining formula. |
| Volume == 0 guard | MFI = 0 | Avoids division by zero; zero-volume bars carry no facilitation. |
| Bar classification | vs previous bar: GREEN (MFI↑ vol↑), FADE (MFI↓ vol↓), FAKE (MFI↑ vol↓), SQUAT (MFI↓ vol↑) | Williams' four-way classification from "Trading Chaos". |
| Unchanged MFI / volume | Counts as "down" (not up) | Classification uses strict > for "up"; an exactly unchanged bar is neither up nor down, and "not up" is the conservative bucket. First bar has no previous bar → type "none". |
| Trend filter | EMA(20) on close | Spec-fixed confirmation: longs only above EMA(20), shorts only below. |
| Squat breakout window | 5 bars after the squat bar (squat bar excluded) | Spec-fixed. Only the most recent squat counts; a newer squat replaces it. |
| Entries | Long: close above squat high within window + close above EMA(20). Short: close below squat low within window + close below EMA(20). | Spec-fixed. |
| Exits | Long: FADE bar or close below EMA(20). Short: FADE bar or close above EMA(20). | Spec-fixed. The ATR stop/trail from the risk layer also applies. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 30 | EMA(20) needs 20 bars + margin; MFI/classification need 2 bars. |

## Spec deviations / interpretation notes

- **Squat not consumed by an entry.** The spec does not say a squat is
  used up once it triggers an entry. Implementation keeps the squat
  active for its full 5-bar window, so if a position exits (e.g. on a
  FADE bar) while the same squat is still in-window, a fresh breakout
  close can re-enter. This is the literal reading of the spec.
- **FADE exit is a per-bar signal, not a position-aware rule.** The
  signal columns mark every FADE bar as an exit for the matching side;
  the harness only acts on it while that side is open, per the shared
  execution convention.
- **Breakout check precedes squat replacement within a bar.** A bar
  that is itself a squat is first tested as a breakout against the
  previous squat, then becomes the active squat. (In practice a close
  above a bar's own high is impossible, so the ordering only matters
  for replacement timing.)
- No other deviations: the MFI formula, four-way classification,
  5-bar window, EMA(20) filter, and exit rules are implemented exactly
  as specified. No PnL-selected tuning; no bug fixes requiring re-runs.
