# Relative Vigor Index — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a
priori from the spec, and the backtest numbers were reported as-is.
Two alternates were run after the fact as a robustness check only;
neither was adopted.

| Parameter | Value | A priori rationale |
|---|---|---|
| RVI numerator | (c-o) + 2*(c1-o1) + 2*(c2-o2) + (c3-o3) | Spec as written (Ehlers' 1-2-2-1 SWMA of close-minus-open). |
| RVI denominator | (h-l) + 2*(h1-l1) + 2*(h2-l2) + (h3-l3) | Spec as written (1-2-2-1 SWMA of high-minus-low). |
| RVI | numerator / denominator; zero denominator -> 0 | Spec as written. |
| Signal | (RVI + 2*RVI1 + 2*RVI2 + RVI3) / 6 | Spec as written (1-2-2-1 weighted average of RVI). |
| Entry | RVI crosses signal (transition only) | The spec's trigger. |
| Exit | opposite cross (plus harness stop/trail) | The spec's exit. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 40 | RVI needs 4 bars; signal needs 4 RVI values (first at bar 6); 40 gives margin. |

## Sweep results (same window, local cache only)

| Config | Trades | Net $ | PF | Fees $ |
|---|---|---|---|---|
| **Shipped direct 4-bar SWMA ratio** | **5248** | **-25796.42** | **0.61** | **17127.83** |
| Alt-A 10-bar SMA-smoothed num/den (platform variant) | 3264 | -20943.83 | 0.67 | 14419.44 |
| Alt-B signal = SMA(4) of RVI | 5072 | -25017.66 | 0.63 | 17309.39 |

Per-coin, Alt-A: BTC -8339.99, ETH -6327.66, HYPE -6276.18.
Per-coin, Alt-B: BTC -9331.51, ETH -7743.92, HYPE -7942.23.
Smoothing the ratio over 10 bars (Alt-A, the MetaTrader/platform
variant) cuts the trade count by ~38% and the loss by ~19%, but
still loses on every coin; equal-weighting the signal (Alt-B) is
barely different from shipped. The loss is structural to trading
RVI/signal crosses at 1h crypto frequency, not to the smoothing
choice. Nothing was changed as a result of the sweep.

## Spec decisions / ambiguities

1. **Direct ratio, no 10-bar SMA smoothing.** The brief defines RVI
   as the 4-bar SWMA numerator divided by the 4-bar SWMA
   denominator. Several platforms (MetaTrader 5, TradingView's
   built-in RVI) additionally average the numerator and denominator
   over 10 bars before dividing (RVI = SMA(Numerator, 10) /
   SMA(Denominator, 10)). That variant was NOT shipped; it was run
   as Alt-A above and also loses.
2. **Zero denominator -> 0, not NaN.** A doji run (h == l) makes
   both numerator and denominator 0; the spec's guard returns 0.
   NaN denominators (the first 3 bars) stay NaN rather than 0, so
   no signal can fire before bar 6.
3. **Cross uses strict inequality on the current bar and
   non-strict on the previous bar** (rvi > signal and prev rvi <=
   prev signal), matching the template's crossed_above semantics.
4. **Attribution note:** Ehlers introduced RVI in Technical
   Analysis of Stocks & Commodities (January 2002) and expanded it
   in "Cybernetic Analysis for Stocks and Futures" (2004). The
   similarly-named Relative *Volatility* Index is Donald Dorsey's
   separate indicator and is not used here.

## What the exits actually did

Shipped run (5248 trades): 4263 trades ended on the opposite-cross
signal and 985 on the harness stop/trail. Positions last only a few
bars on average — RVI and its signal cross almost every other bar
at 1h frequency, so the strategy is almost always in the market and
pays fees on every whipsaw.

No bug fixes requiring re-runs, no PnL-selected tuning.
