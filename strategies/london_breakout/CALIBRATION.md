# London Session Breakout — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Range hours | 00:00–08:00 UTC (hours 0–7) | The spec's adaptation: the published 00:00–08:00 London range read in fixed UTC. |
| Entry window | 08:00–12:00 UTC (hours 8–11) | The spec's adaptation of the published 08:00–12:00 London entry window. |
| Time exit | 16:00 UTC bar | The spec's adaptation of the published 16:00 London time exit. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | The range needs one full day to seed; 60 bars gives margin over the first partial day. |

## Spec decisions / ambiguities

1. **Fixed UTC hours, winter/GMT reading.** The published rule is
   in London time; crypto trades 24/7 and the candles are UTC, so
   the shipped adaptation uses fixed UTC hours (range 00:00–08:00,
   entry 08:00–12:00, exit 16:00). This is the winter/GMT reading
   of the rule: London = UTC in winter, BST shifts +1h in summer.
   Fixed UTC was chosen for reproducibility over a London-time
   clock that would shift mid-window. In summer months the shipped
   window is effectively one hour earlier in London terms.
2. **Entry is on the close, not the high/low.** The published rule
   enters when a bar's high goes above the range high (or low
   below the range low). The batch spec fixes the entry as "close
   > range_high" / "close < range_low" on the break bar, and the
   harness executes at the next bar's open — shipped as specified.
   A close-based break is strictly narrower than a wick-based
   break, so fewer entries than the literal published rule.
3. **Both-sides break uses the bar's high/low.** With a
   close-based entry a single close cannot break both sides, so
   the "first bar breaks both sides, skip the day" rule is
   implemented on the bar's wicks: if the first break bar's high
   is above the range high AND its low is below the range low, no
   entry that day. This preserves the published skip rule under
   the close-based entry.
4. **First break only, per day.** Only the first break bar of the
   day (in the 08:00–12:00 window) can enter; later breaks the
   same day are ignored. The day is keyed on the UTC date of the
   bar.
5. **Time exit fires on the 16:00 bar.** The exit signal is set on
   the bar with hour == 16, so the harness exits at the 17:00
   open — one bar after the published 16:00 exit. This is the
   harness's next-bar-open execution convention, not a rule
   change; the range columns are NaN at hour 16, so the time exit
   is the only exit that can fire there.
6. **The published 1R target / range-other-side stop are NOT
   separate exits.** The spec's exits are the opposite-side break
   and the 16:00 time exit; the batch-standard risk layer (2xATR
   stop, 2.5xATR trail, 120-bar max hold) is applied on top, per
   the batch instruction. No 1R take-profit is implemented
   (target_atr_mult=None).
7. **Harness stop/trail as an additional exit.** As above, the
   2xATR stop / 2.5xATR trail apply on top of the spec exits.

## What the exits actually did

Shipped run (345 trades): 179 trades ended on the harness stop/trail
and 166 on a signal exit (BTC 63 stop / 46 signal, ETH 55 / 47, HYPE
61 / 73). The split is nearly even: about half the session breaks
reverse into the 2xATR stop before the 16:00 time exit or the
opposite-side break fires, and the other half exit on the time exit /
opposite break — neither exit saves the trade on average.

No bug fixes requiring re-runs, no PnL-selected tuning.
