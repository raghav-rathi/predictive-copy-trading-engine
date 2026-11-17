# RSI Volume Confirmation — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| RSI period | 14 | Wilder's standard RSI period, from the spec. |
| RSI midline | 50 | The spec's momentum midline; a cross is a strict crossing (previous bar on one side, current bar on the other). |
| Volume multiple | > 1.25x trailing mean volume | The spec's confirmation threshold. Strictly greater (exactly 1.25x does not confirm). |
| Volume mean | Previous 20 bars (shifted by 1) | The spec says "previous 20 bars, shifted by 1"; the current bar's own volume must not dilute the mean it is compared against. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | RSI(14) + 20-bar volume mean need ~35 bars to seed; 60 gives margin. |

## Spec decisions / ambiguities

1. **A cross is a strict crossing of 50.** RSI exactly 50 on the
   previous bar does not count as being on either side; the
   `crossed_above`/`crossed_below` helpers in `strategies/base.py`
   implement this (current bar strictly past the level, previous
   bar at or on the far side).
2. **The volume filter applies to entries only.** Exits are pure
   RSI reverse crosses, per spec; a low-volume reverse cross still
   exits.
3. **Harness stop/trail as an additional exit.** The spec's exits
   are the RSI reverse crosses; the batch-standard risk layer
   (2xATR stop, 2.5xATR trail, 120-bar max hold) is applied on
   top, per the batch instruction.

## What the exits actually did

Shipped run (675 trades): exits split nearly evenly — 318 on the
RSI reverse-cross signal and 357 on the harness stop/trail (BTC
145 stop / 96 signal, ETH 116 / 126, HYPE 96 / 96). The signal
exit does real work here, unlike in trend-filter strategies; the
loss comes from the entry side (26.2% win rate), not from exits
failing to fire.

No bug fixes requiring re-runs, no PnL-selected tuning.
