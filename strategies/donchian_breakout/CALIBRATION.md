# Donchian Channel Breakout — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a
priori from the spec, and the backtest numbers were reported as-is.
Two alternates were run after the fact as a robustness check only;
neither was adopted.

| Parameter | Value | A priori rationale |
|---|---|---|
| Donchian channel | 20 bars, prior-bar window (bars i-20..i-1) | Canonical Turtle System 1 entry channel; the channel is built from completed bars only, so the close is compared against a level that excludes the current bar. |
| Entry | close > prior-20 high / close < prior-20 low, transition only | A breakout is the first close beyond the channel; a close already beyond it on the prior bar is not a new breakout. |
| Exit | opposite 20-bar extreme, OR close beyond the prior-10-bar extreme (Turtle 10-bar exit) | Turtle System 1 exit rule: longs exit on a 10-day low, shorts on a 10-day high. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 40 | Channel needs 20 bars (+1 shift); 40 gives margin over the ATR(14) seed as well. |

## Sweep results (same window, local cache only)

| Config | Trades | Net $ | PF | Fees $ |
|---|---|---|---|---|
| **Shipped Chan20 / Exit10** | **667** | **-2097.76** | **0.93** | **5062.32** |
| Alt-A Chan55 / Exit20 | 369 | -3259.15 | 0.81 | 2609.22 |
| Alt-B Chan10 / Exit5 | 1012 | -4652.52 | 0.89 | 7224.49 |

Per-coin, Alt-A: BTC -1239.38, ETH -723.71, HYPE -1296.06.
Per-coin, Alt-B: BTC -3275.28, ETH -392.16, HYPE -985.08.
Both alternates lose more than the shipped config while Alt-B trades
far more often (1,012 trades, $7,224 of fees). The slower Turtle
System 2 channel (55/20) does not rescue the idea on this window
either. Nothing was changed as a result of the sweep.

## Spec decisions / ambiguities

1. **Channel excludes the current bar.** The spec says upper = max
   high of the PRIOR 20 bars (bars i-20..i-1). Implemented as
   `rolling(20).max().shift(1)`, so a close can break the channel
   on the bar that prints the new high — the classic Turtle reading
   (the breakout bar's own high is not part of the channel it
   breaks). Including the current bar would make a close-above
   breakout impossible.
2. **Transition is judged against the prior bar's own channel.**
   Long entry requires close[i] > upper[i] AND close[i-1] <=
   upper[i-1] (not close[i-1] <= upper[i]); the "then-current"
   upper is the one in force on the previous bar.
3. **Exits are level conditions, not transitions.** Long exit is
   true on any bar the close sits below the lower channel or the
   prior-10-bar low; the harness exits on the first such bar, so
   the distinction from a transition-only exit does not change
   backtest results.
4. **No Turtle skip rule.** The original System 1 skipped a
   breakout if the previous System 1 breakout would have been a
   winner. The assigned spec did not include it, so it was not
   implemented; adding it would be a different strategy.
5. **The 10-bar exit usually dominates the 20-bar exit.** The
   prior-10-bar low is >= the prior-20-bar low, so the Turtle exit
   fires first on a drift down; the 20-bar exit only matters on a
   gap straight through both levels.

## What the exits actually did

Shipped run (667 trades): 595 trades ended on the harness stop /
trail and only 72 on the Donchian/Turtle signal exit. Entries fire
roughly once per 27 bars per coin, then the position is usually
stopped out before the trend exit can trigger — the breakout has no
follow-through on this window.

No bug fixes requiring re-runs, no PnL-selected tuning.
