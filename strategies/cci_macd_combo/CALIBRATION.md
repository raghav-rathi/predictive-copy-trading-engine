# CCI + MACD Combo — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| CCI period | 14 | The spec's CCI(14); the standard CCI lookback. |
| Typical price | (h + l + c) / 3 | The spec's typical price. |
| Mean deviation | 14-bar rolling mean of \|TP - SMA(TP, 14)\| | The TradingView `ta.cci` definition: the deviation series is smoothed with the same 14-bar window. |
| CCI constant | 0.015 | Lambert's constant from the spec; scales CCI so ±100 marks the usual overbought/oversold band. |
| MACD | 12 / 26 / 9 on the raw close | The spec's MACD; computed on the raw close, not the typical price. |
| Entry thresholds | CCI crosses -100 up (long) / +100 down (short) | Per spec; the cross must be a genuine crossing, not merely being beyond the level. |
| MACD filter | MACD line > signal (long) / < signal (short), strict | Per spec, evaluated on the entry bar. |
| Exit | CCI crosses back through 0 | Per spec: long exits when CCI crosses below 0, short when it crosses above 0. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | CCI is first defined at bar 26 (14 for the SMA + 14 defined deviations) and MACD needs ~35 bars; 60 gives margin. |

## Spec deviations

1. **Mean deviation is a rolling mean of per-bar deviations.**
   The spec says "mean deviation" without pinning the formula.
   The shipped code follows TradingView `ta.cci`: mean dev =
   SMA(|TP - SMA(TP, 14)|, 14). The alternative textbook reading
   (mean of |TP_i - current SMA| over the window) would make CCI
   defined from bar 13 instead of bar 26 and would change values
   slightly; the shipped reading is the one the cited sources'
   platform implements.
2. **Zero mean deviation gives NaN CCI.** A flat typical price
   makes the denominator zero; CCI is NaN and produces no signal
   rather than an arbitrary 0 or infinite value.
3. **Harness stop/trail as an additional exit.** The batch-standard
   risk layer (2xATR stop, 2.5xATR trail, 120-bar max hold) is
   applied on top of the spec's exit, per the batch instruction.
   45 of 87 trades ended on the stop/trail, 42 on the signal exit.
4. **MACD filter is strict.** MACD line exactly equal to its signal
   line is neither bullish nor bearish; no entry fires on that bar.
   A measure-zero event on real data.

No bug fixes requiring re-runs, no PnL-selected tuning.
