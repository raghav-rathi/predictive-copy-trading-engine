# New York Open Momentum

ICT Power of 3 applied to the New York open: the first hour sets the
range, the expansion leg breaks it, and the move is exited at the
end of the New York session.

## Rules

- **New York open:** fixed at 13:00 UTC (winter/GMT reading — crypto
  is 24/7, so this is a clock rule, not a real market open; see
  CALIBRATION.md).
- **First-hour range:** high/low of the 13:00 UTC bar (13:00-14:00).
- **Long entry:** a close above the first-hour high during the
  14:00-17:00 UTC window (the bars opening 14:00, 15:00 and 16:00);
  only the first break of the day per side fires.
- **Short entry:** a close below the first-hour low during the same
  window; first break per side only.
- **Long exit:** the close of the 21:00 UTC bar (time exit, filled at
  the next bar's open by the harness) OR an opposite short break.
- **Short exit:** the close of the 21:00 UTC bar OR an opposite long
  break.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 48 bars.
- Warmup 60 bars.

All computation is causal, so signals on bar i use only data through
bar i's close. The first-hour range is only visible from the 13:00
bar itself — bars earlier in the day carry NaN, never a range that
has not formed yet.

## Sources

- Proptary, "Power of 3 (ICT)":
  https://www.proptary.com/education/power-of-3-ict

Paper only, no live execution.
