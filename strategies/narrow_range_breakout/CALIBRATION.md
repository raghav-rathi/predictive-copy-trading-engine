# Narrow-Range Breakout (NR7) — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| NR window | 7 bars incl. itself | Spec (Toby Crabel NR7). |
| Setup validity | 24 bars after the setup bar | Spec. |
| Trend filter | SMA50 vs SMA200 at the setup bar | Spec. |
| ATR window / stop / trail / max hold | 14 / 2.0x / 2.5x / 120 bars | Batch-standard risk layer. |
| WARMUP | 250 | Indicator warmup (SMA200) + margin. |

Implementation notes (closest faithful variant, no spec change to
the trading rules):

- Ties count as setups: a bar whose range merely equals the 7-bar
  minimum is an NR7 bar, per the literal "smallest of the last 7
  bars". On 1h crypto data this makes setups frequent.
- The setup governs bars i+1..i+24 after the setup bar (the setup
  bar itself never trades off its own levels: the setup columns are
  shifted by one bar).
- Extra indicator column `nr_setup_dir` (+1 / -1 / NaN) records the
  trend direction at the setup bar. The listed setup high/low
  columns alone cannot retain it, and the spec's trend filter is
  evaluated at the setup bar, not at the entry bar.
- Exit "a short setup triggers" is a fresh NR7 bar with SMA50 <
  SMA200 on the current bar (mirror for longs).

No bug fixes requiring re-runs, no PnL-selected tuning.
