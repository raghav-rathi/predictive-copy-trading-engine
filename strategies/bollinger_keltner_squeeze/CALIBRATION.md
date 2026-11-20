# Bollinger/Keltner Squeeze — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a
priori from the spec, and the backtest numbers were reported as-is.
Two alternates were run after the fact as a robustness check only;
neither was adopted.

| Parameter | Value | A priori rationale |
|---|---|---|
| Bollinger Bands | 20 bars, 2.0 std, SMA mid | Canonical TTM Squeeze / Carter construction. |
| Keltner Channels | 20 bars, 1.5 x ATR(14), EMA mid | Canonical TTM Squeeze: KC mid is an EMA(20), ATR(14) per the spec. |
| Squeeze ON | bb_upper < kc_upper AND bb_lower > kc_lower (strict) | The bands must sit strictly inside the channels; touching is not a squeeze. |
| Momentum | 20-bar OLS fitted value of close - ((20-bar high-low midpoint + SMA(20)) / 2) | TTM momentum histogram definition; fitted value at bar i (mean + slope x 9.5). |
| Fire | first bar squeeze turns OFF after being ON | The spec's trigger; a squeeze that stays OFF does not re-fire. |
| Direction | long if momentum > 0, short if momentum < 0 on the fire bar | Momentum sign is the breakout direction. |
| Exit | opposite signal only (plus harness stop/trail) | The spec's exit; no squeeze-re-entry exit. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 40 | BB/KC need 20 bars; momentum needs 20 bars for x plus a 20-bar regression window (first valid at bar 38); 40 gives margin. |

## Sweep results (same window, local cache only)

| Config | Trades | Net $ | PF | Fees $ |
|---|---|---|---|---|
| **Shipped BB20 / KC 1.5 / MOM20** | **379** | **366.04** | **1.02** | **3405.32** |
| Alt-A BB15 / KC15 / MOM15 | 570 | -2128.62 | 0.92 | 4319.10 |
| Alt-B KC mult 2.0 | 506 | -3134.58 | 0.87 | 3870.55 |

Per-coin, Alt-A: BTC -2397.99, ETH -1109.63, HYPE +1379.01.
Per-coin, Alt-B: BTC -1952.28, ETH -271.04, HYPE -911.26.
Both alternates lose money while trading more often — the shipped
config's nominal win does not survive even a small parameter change,
which reinforces the BACKTEST.md verdict (no robust edge). Nothing
was changed as a result of the sweep.

## Spec decisions / ambiguities

1. **Keltner mid is EMA(20), Bollinger mid is SMA(20).** The spec
   says "Keltner(20, 1.5xATR(14)) around SMA(20)"; the shipped
   reading follows the standard Carter/TTM construction (EMA for
   Keltner, SMA for Bollinger). Using SMA for both would change
   squeeze timing slightly.
2. **Momentum regression is fit on trailing x values only.** x
   itself needs 20 bars, so the first momentum value appears at
   bar 38, not bar 19 — the regression window must be full of
   defined x values (pandas `min_periods` counts non-NaN values).
   WARMUP 40 covers this.
3. **Squeeze state is False while bands are undefined** (first 19
   bars), so no fire can occur before bar 20.
4. **Exit is the opposite fire only.** A squeeze turning back ON
   does not exit an open trade; the harness stop/trail/max-hold
   does most of the exiting here (360 of 379 exits).

## What the exits actually did

Shipped run (379 trades): 360 trades ended on the harness stop /
trail and only 19 on the opposite signal. The entry fires rarely
(~1 trade per 16 bars per coin) and the position then rides until
the stop or the 120-bar max hold — there is no profitable
follow-through exit in the signal layer on this window.

No bug fixes requiring re-runs, no PnL-selected tuning.
