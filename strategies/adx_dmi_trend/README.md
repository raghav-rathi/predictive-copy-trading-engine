# Wilder ADX/DMI Trend System

Wilder's own trend system from *New Concepts in Technical
Trading Systems* (1978): trade only when the market is
trending, as judged by ADX, and take the direction from the DI
cross. The ADX gate is the whole point — Wilder designed the
system to sit out trendless markets rather than chop in them.

## Rule (long)

```
ADX(14) > 25  (Wilder's trend-strength gate)
AND +DI crosses above -DI  (transition only)
```

- **Exit long:** the opposite cross (-DI crosses above +DI) OR
  ADX falling below 20.
- **Short mirror:** -DI crosses above +DI while ADX > 25; exit
  on the opposite cross (+DI above -DI) OR ADX below 20.
- **Flip:** an opposite setup while in a position exits and
  enters the other side on the same bar (an opposite cross is
  by construction the long exit condition, so the flip follows
  from the exit rule).

## 1h scaling (documented)

- ADX(14), +DI, -DI are used exactly as Wilder published — no
  rescaling. On 1h bars the 14-bar smoothing is a ~14-hour
  memory, so the system reacts to intraday trend structure
  rather than the multi-week trends Wilder traded daily.
- The 25/20 gate/exit pair is Wilder's own hysteresis: enter
  only above 25, exit only below 20, so a wobble between 20 and
  25 does not churn the position.

## Honest flag: the ADX > 25 gate is Wilder's own rule — and 1h crypto spends long stretches below it

The gate is not our conservatism; it is the system. ADX on 1h
crypto sits below 25 for long stretches of chop, and during
those stretches this system is flat by design — no trades, no
signals, nothing to report. The 278 trades in the backtest all
come from the minority of the window where a 1h trend actually
registered. A trader expecting daily action from this system on
1h bars will be disappointed; that is Wilder working as
intended, not a bug. See BACKTEST.md.

## Risk

2×ATR(14) harness stop as a backstop (the signal-level DI-cross
/ ADX exit is the real stop), no trail, no target, 168-bar
(~7-day) max hold, 1% risk per trade, 3× leverage cap.
WARMUP = 40 bars (ADX(14) needs ~14 bars to seed the DIs plus
smoothing time for DX/ADX; 40 covers it).

Source: J. Welles Wilder, *New Concepts in Technical Trading
Systems* (1978) —
https://en.wikipedia.org/wiki/Average_directional_movement_index.
