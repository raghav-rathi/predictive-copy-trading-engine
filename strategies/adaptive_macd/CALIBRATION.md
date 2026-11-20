# Adaptive MACD — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a
priori from the spec, and the backtest numbers were reported as-is.
Two alternates were run after the fact as a robustness check only;
neither was adopted.

| Parameter | Value | A priori rationale |
|---|---|---|
| Efficiency ratio window | 10 bars | Kaufman's ER window from the spec; ER = \|close - close[10]\| / sum of \|diffs\| over 10 bars. |
| Fast adaptive EMA range | 2..12 | KAMA-style: SC_fast = (ER*(2/3 - 2/13) + 2/13)^2. |
| Slow adaptive EMA range | 5..26 | KAMA-style: SC_slow = (ER*(2/6 - 2/27) + 2/27)^2. |
| Adaptive EMA seeding | close on the first ER-valid bar (bar 10) | Standard KAMA seeding; no lookahead (uses close[10] only). |
| Signal line | 9-bar EMA of MACD (alpha 2/10), seeded with the first MACD value | Standard MACD signal construction. |
| Entry / exit | MACD cross above/below signal; exit on the opposite cross | The spec's rule (Appel MACD cross). |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | ER needs 10 bars and the adaptive EMAs need time to separate; 60 gives margin. |

## Sweep results (same window, local cache only)

| Config | Trades | Net $ | PF | Fees $ |
|---|---|---|---|---|
| **Shipped ER10** | **998** | **-5587.65** | **0.87** | **7210.22** |
| Alt-A ER5 | 1270 | -5583.49 | 0.89 | 9017.58 |
| Alt-B ER20 | 841 | -3453.41 | 0.91 | 6457.20 |

Per-coin, Alt-A (ER5): BTC -3716.83, ETH -1928.45, HYPE +61.79.
Per-coin, Alt-B (ER20): BTC -2233.33, ETH -2293.35, HYPE +1073.27.
A longer ER window (20) loses less by trading less, but still loses
on every coin except HYPE — the direction of the result is stable
across the sweep, which supports the LOSER verdict rather than a
parameter accident. Nothing was changed as a result of the sweep.

## Spec decisions / ambiguities

1. **ER denominator is the sum of |close diffs| over the trailing
   10 bars** (bars i-9..i), matching the 10-bar numerator
   |close[i] - close[i-10]|. On a flat stretch the denominator is
   0 and ER is defined as 0 (slowest smoothing), not NaN.
2. **SC ranges are the spec's (2,12) fast and (5,26) slow.**
   The task text also mentions "(2,30) and (5,60)" as a question;
   the shipped reading uses the explicit SC formulas given in the
   task (2/3-2/13 and 2/6-2/27), i.e. ranges 2..12 and 5..26.
3. **Signal EMA is computed by hand recursion**, seeded with the
   first MACD value, so no NaN handling of pandas `ewm` over a
   NaN-prefixed series is involved.
4. **Crosses use the base `crossed_above`/`crossed_below`
   helpers** (strict inequality vs the prior bar), so a MACD line
   sitting exactly on its signal does not fire.

## What the exits actually did

Shipped run (998 trades): 743 trades ended on the harness stop /
trail and 255 on the opposite cross. The stop dominates — MACD
crosses on 1h crypto reverse quickly, and the 2xATR stop catches
most positions before the opposite cross arrives.

No bug fixes requiring re-runs, no PnL-selected tuning.
