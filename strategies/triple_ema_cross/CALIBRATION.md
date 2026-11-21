# Triple EMA Crossover — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a
priori from the spec, and the backtest numbers were reported as-is.
Two alternates were run after the fact as a robustness check only;
neither was adopted — including Alt-A, which was profitable (see
below).

| Parameter | Value | A priori rationale |
|---|---|---|
| EMAs | EMA(5) fast, EMA(13) mid, EMA(50) slow (pandas ewm, span=n, adjust=False) | The assigned 5/13/50 triple; 5 and 13 are the fast Fibonacci pair, 50 is the trend filter. |
| Entry trigger | EMA(5) crosses EMA(13) (transition only) | The fast/mid cross is the timing signal. |
| Entry filter | long requires EMA5 > EMA13 > EMA50; short requires EMA5 < EMA13 < EMA50 on the cross bar | The slow EMA must confirm the trend direction; a cross against the stack is not traded. |
| Exit | EMA(5) crosses back through EMA(13) | The spec's exit; symmetric with the entry trigger. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 70 | Slowest EMA needs 50 bars; 70 gives margin. |

## Sweep results (same window, local cache only)

| Config | Trades | Net $ | PF | Fees $ |
|---|---|---|---|---|
| **Shipped 5/13/50** | **539** | **-5244.33** | **0.75** | **4054.49** |
| Alt-A 9/21/55 | 295 | +2226.91 | 1.17 | 2670.80 |
| Alt-B 5/8/13 | 716 | -5346.98 | 0.80 | 5620.42 |

Per-coin, Alt-A: BTC +501.78, ETH +1031.79, HYPE +693.35.
Per-coin, Alt-B: BTC -2557.44, ETH -448.21, HYPE -2341.34.
Alt-A (9/21/55) wins on all three coins while the shipped 5/13/50
loses on all three — the result is extremely parameter-sensitive,
which is itself the finding: the shipped config has no robust edge,
and the Alt-A win is a single alternate out of two, not evidence to
adopt it. Adopting 9/21/55 because it happened to win on this one
window would be PnL-selected tuning, so the shipped 5/13/50 stands
as the reported result. Nothing was changed as a result of the sweep.

## Spec decisions / ambiguities

1. **Cross is judged bar-to-bar on EMA values.** Cross-up is
   EMA5[i] > EMA13[i] AND EMA5[i-1] <= EMA13[i-1]; the stack
   alignment (EMA13 vs EMA50) is checked on the cross bar itself.
2. **Exit is the cross back, with no stack condition.** A long
   exits as soon as EMA(5) crosses back below EMA(13), even if
   EMA(13) is still above EMA(50). The spec's exit is the cross
   alone.
3. **Exit columns mirror entries.** long_exit is the cross-down
   column and short_exit the cross-up column, so a cross that
   exits one side is the entry signal for the other side — the
   same construction as the template's opposite-signal exit.
4. **EMA seed.** `strategies.base.ema` uses pandas ewm with
   `min_periods=n`, so EMA(50) is undefined for the first 49 bars;
   WARMUP 70 keeps the harness out of that region.

## What the exits actually did

Shipped run (539 trades): 289 trades ended on the harness stop /
trail and 250 on the cross-back signal exit — the most signal-driven
exits in batch 42. The cross-back exit is doing its job (cutting
trades quickly), but the entries that precede it lose often enough
(24.1% win rate) that fast exits just realize small losses sooner.

No bug fixes requiring re-runs, no PnL-selected tuning.
