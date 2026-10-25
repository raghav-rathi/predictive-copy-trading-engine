# Classic Pivot Breakout

The original floor-trader pivot formula, computed from the prior bar
on 1h candles: PP = (H+L+C)/3, R1 = 2*PP - L, S1 = 2*PP - H. Traded as
a breakout system: long on a close above R1, short on a close below
S1, exit on a close back through PP. Using the prior bar (not the
prior day) keeps the levels fresh every hour.

## Rules

- Long entry: close crosses above R1 (from the prior bar's HLC)
- Short entry: close crosses below S1
- Exit: close crosses back through PP
- Risk: 1.5xATR stop, 2xATR trail, no fixed target, 72-bar (3-day)
  max hold, 1% equity risk per trade, 3x leverage cap

## Why this parameterization

Pivot levels from a single bar are tight — one bar's range — so the
stop is the tighter house variant (1.5xATR) and the hold is short
(3 days). The thesis is that hourly pivot breaks mark real intraday
turns. The backtest says otherwise (see BACKTEST.md), and the reason
is structural: a level built from one bar's range is barely a level
at all, so it breaks constantly.

Source: classic floor-trader pivot formula (PP/R1/S1 from
prior-period HLC).
