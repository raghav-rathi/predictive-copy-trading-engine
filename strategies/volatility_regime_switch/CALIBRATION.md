# Volatility Regime Switch — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| ATR window | 14 | The spec's ATR(14). |
| Percentile window | 100 bars | The spec's trailing 100 bars. |
| Expansion / compression thresholds | > 0.60 / < 0.40 | The spec's percentile bands; 0.40–0.60 is the middle regime. |
| Percentile rank definition | fraction of the last 100 ATR values ≤ current ATR (ties count) | The spec's "percentile rank"; inclusive of the current bar, so a perfectly constant ATR ranks 1.0 (verified in the flat-frame test — entries still need a real breakout, which flat prices never print). |
| Donchian length | 20 | The spec's Donchian(20). |
| Prior high/low | Donchian level shifted by 1 bar (excludes the current bar) | Load-bearing, per the spec note: a trailing high including the current bar can never be broken by the close. Verified by a dedicated test (`test_prev_high_excludes_current_bar`). |
| Bollinger | (20, 2) | The spec's Bollinger(20, 2), via `base.bollinger`. |
| Expansion exit | close back inside the channel midpoint, or the opposite break | The spec's "exit on close back inside the channel midpoint or opposite break"; midpoint is (prev_high + prev_low) / 2. |
| Compression exit | close back to the Bollinger mid | The spec's "exit on close back above the mid" (long) / "below the mid" (short). |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 120 | 100-bar percentile + indicator warmup, per the spec. `atr_pct` first becomes valid at bar 112 (the 100-bar window must sit fully on valid ATR values, and ATR needs 14 bars). |

## Spec decisions / ambiguities

1. **Entries are level rules, not cross events.** "Long on a
   close above the prior 20-bar high" fires on every bar the
   close sits beyond the level, not just the crossing bar. The
   harness takes one position at a time, so repeat signals
   while flat are harmless; the entry bar is the first bar the
   level holds. The same applies to the Bollinger fades.
2. **Exits follow the regime in force.** A trade opened in
   expansion is exited by expansion rules while the regime
   persists; if the regime flips to compression mid-trade, the
   compression exit (close back to the Bollinger mid) takes
   over. In the middle regime there is no signal exit and the
   harness stop/trail/max-hold carries the trade.
3. **"Back inside the channel midpoint"** is read as a close
   below the midpoint for a long (above it for a short). The
   opposite break (close below the prior low for a long) is an
   additional exit clause, per the spec.
4. **No bug fixes requiring re-runs, no PnL-selected tuning.**

## What the exits actually did

Shipped run (785 trades): 508 exits on the harness stop/trail,
277 on signal exits. The signal exits fire a meaningful share
of the time (the midpoint / Bollinger-mid exits work as
designed), but the stop still dominates — the level-based
entries put the strategy into trades that are usually stopped
out before the exit leg pays.
