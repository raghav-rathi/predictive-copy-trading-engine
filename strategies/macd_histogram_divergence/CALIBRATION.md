# MACD Histogram Divergence — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a
priori from the spec, and the backtest numbers were reported as-is.
Two alternates were run after the fact as a robustness check only;
neither was adopted.

| Parameter | Value | A priori rationale |
|---|---|---|
| MACD | EMA(12) − EMA(26) of close; signal EMA(9) of MACD; hist = MACD − signal | Gerald Appel MACD(12, 26, 9), canonical. |
| Swing pivot | bar i is a swing low if l[i] is the min of l[i−2..i+2] (and strictly below l[i−1]); swing high is the mirror on h | Batch spec; the strict-below-previous-bar rule breaks ties toward the first occurrence. |
| Confirmation | pivot is evaluated at bar i+2 only | Batch spec; causal — the signal fires on the confirmation bar, using data through that bar only. |
| Divergence lookback | previous confirmed pivot within the last 60 bars | Batch spec. |
| Bullish divergence | confirmed swing low LOWER than the previous one, hist at that low HIGHER than hist at the previous low, AND hist turns up (hist[j] > hist[j−1]) on the confirmation bar j | Batch spec. |
| Bearish divergence | mirror: higher swing high, lower hist, hist turns down on the confirmation bar | Batch spec. |
| Long exit / short exit | opposite divergence confirmation OR hist crosses below / above 0 | Batch spec. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 80 | MACD(12, 26, 9) is first defined ~bar 33; a divergence needs two pivots up to 60 bars apart plus 2-bar confirmation; 80 gives margin. |

## Sweep results (same window, local cache only)

| Config | Trades | Net $ | PF | Fees $ |
|---|---|---|---|---|
| **Shipped pivot ±2 / lookback 60** | **475** | **-2214.41** | **0.90** | **3555.68** |
| Alt-A lookback 30 | 475 | -2214.41 | 0.90 | 3555.68 |
| Alt-B pivot half-width 3 | 413 | -1628.22 | 0.91 | 3128.18 |

Per-coin, Alt-A: identical to shipped on every coin.
Per-coin, Alt-B: BTC -1930.53, ETH -1163.99, HYPE 1466.29.
Alt-A is byte-identical to the shipped run: no divergence pair in
this window is 31–60 bars apart, so the lookback change binds
nowhere. Alt-B (wider pivots, fewer and later signals) loses less
(−$1,628.22) but is still negative on BTC and ETH. Nothing was
changed as a result of the sweep.

## Spec decisions / ambiguities

1. **"Hist turns up (hist[i] > hist[i−1]) on the confirmation
   bar"** is read with i = the confirmation bar j = pivot bar + 2
   (hist[j] > hist[j−1]), not the pivot bar itself. The pivot-bar
   reading would compare hist at the low against the bar before
   the low, which is not a turn-up at the moment the signal fires.
2. **"Hist at that low" means hist at the pivot bar**, compared
   against hist at the previous pivot bar — not hist at the
   confirmation bar.
3. **Pivot ties:** a flat stretch has many equal minima; the
   l[i] < l[i−1] requirement makes only the first bar of a flat
   bottom a pivot, so flat bars generate no pivots and no
   divergences.
4. **The 60-bar lookback is measured between pivot bars**, not
   confirmation bars.
5. **A divergence is a single-bar signal on the confirmation
   bar.** If the next bar also confirms a pivot, it is evaluated
   independently against the updated pivot history.

## What the exits actually did

Shipped run (475 trades): 318 trades ended on the harness stop /
trail and 157 on a signal exit (opposite divergence or histogram
zero-line cross). Divergence entries are infrequent (~1 trade per
13 bars per coin) and the position then mostly rides to the stop —
the signal exit is not what closes most trades.

No bug fixes requiring re-runs, no PnL-selected tuning.
