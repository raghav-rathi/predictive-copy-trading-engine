# Donchian EMA Filter — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a
priori from the spec, and the backtest numbers were reported as-is.
A small sweep (2 alternate settings, run and reported honestly below)
was used only to check robustness, not to select the shipped config.

| Parameter | Value | A priori rationale |
|---|---|---|
| Donchian channel | 20 bars, previous bars only (level on bar i = highest high / lowest low of bars i-20..i-1) | The spec's Donchian(20); the current bar is excluded so the breakout is measured against a level known before the bar opens. |
| EMA filter | EMA(50) of close | The spec's trend filter: only take breakouts in the direction of the 50-bar trend. |
| Exit | prior 10-bar low / high (Turtle System 1 exit) | The spec's exit: a long exits on a close below the lowest low of the previous 10 bars, a short on a close above the highest high of the previous 10 bars. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | EMA(50) needs 50 bars; 60 gives margin. |

## Sweep (robustness check only — shipped config unchanged)

| Setting | Combined trades | Win% | Net $ | PF | Fees $ |
|---|---|---|---|---|---|
| **Shipped: Donchian 20 / EMA 50 / exit 10** | **660** | **33.5%** | **-3120.47** | **0.90** | **5036.00** |
| Alt A: Donchian 10 / EMA 20 / exit 5 | 1022 | 33.4% | -5796.68 | 0.86 | 7219.58 |
| Alt B: Donchian 40 / EMA 100 / exit 20 | 446 | 30.9% | -3778.03 | 0.82 | 3218.46 |

Both alternates lose more than shipped, with worse profit factors
(0.86 and 0.82 vs 0.90). The faster variant overtrades (1,022
trades, $7,219.58 fees); the slower variant trades less but wins
less often (30.9%). No setting shows an edge, so the shipped
config was kept as specified.

## Spec decisions / ambiguities

1. **Breakout levels exclude the current bar.** Donchian(20) on
   bar i uses bars i-20..i-1 (rolling max/min shifted by 1). A
   bar's own high can never trigger its own breakout — the entry
   requires the close to exceed a level set entirely by prior
   bars. Same for the 10-bar exit levels.
2. **Strict inequalities.** A close exactly at the prior 20-bar
   high (or low) is not a breakout; the entry needs a close
   strictly beyond the level, and strictly beyond EMA(50).
3. **The EMA filter can block a genuine breakout.** After a
   decline, a close above the prior 20-bar high may still sit
   below EMA(50) — the trade is skipped, by design. The unit
   test constructs exactly this case.
4. **Hourly translation of a daily system.** Turtle System 1 used
   20-day breakouts and 10-day exits on daily futures. Here the
   same numbers are bars on 1h candles (~20 hours / ~10 hours),
   which is a much shorter horizon than the original — the
   backtest shows the 10-bar exit almost never fires (69 of 660
   trades), because the 2xATR stop gets hit first.

## What the exits actually did

Shipped run (660 trades): 591 trades ended on the harness stop /
trail and only 69 on the Turtle signal exit. The signal exit is
nearly vestigial at this horizon: breakouts fail into the stop
before price can close back through the 10-bar level.

No bug fixes requiring re-runs, no PnL-selected tuning.
