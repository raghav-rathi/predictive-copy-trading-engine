# On-Balance Volume Breakout — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a
priori from the spec, and the backtest numbers were reported as-is.
Two alternates were run after the fact as a robustness check only;
neither was adopted.

| Parameter | Value | A priori rationale |
|---|---|---|
| OBV | OBV[0] = 0; +v on up closes, -v on down closes, unchanged on equal closes | Joseph Granville's On-Balance Volume definition (Investopedia formula). |
| Breakout lookback | 20 bars, prior-bar window (bars i-20..i-1) | Same 20-bar breakout horizon as the Donchian channel in this batch; a round, canonical lookback for a range breakout. |
| Entry | OBV closes above its prior-20-bar high / below its prior-20-bar low, transition only | A breakout is the first close beyond the OBV extreme; a close already beyond it on the prior bar is not a new breakout. |
| Exit | OBV closes below its prior-20-bar low (longs) / above its prior-20-bar high (shorts) | The opposite OBV extreme; symmetric with the entry. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 40 | OBV extremes need 20 bars (+1 shift); 40 gives margin. |

## Sweep results (same window, local cache only)

| Config | Trades | Net $ | PF | Fees $ |
|---|---|---|---|---|
| **Shipped OBV20** | **909** | **-1847.30** | **0.96** | **6844.59** |
| Alt-A OBV10 | 1385 | -7394.92 | 0.86 | 9054.42 |
| Alt-B OBV55 | 525 | -2420.70 | 0.90 | 3913.80 |

Per-coin, Alt-A: BTC -4135.08, ETH -2259.74, HYPE -1000.10.
Per-coin, Alt-B: BTC -466.52, ETH -746.42, HYPE -1207.77.
Both alternates lose more than the shipped config. The fast 10-bar
lookback is much worse (1,385 trades, $9,054 of fees — the OBV
extreme churns and the strategy overtrades); the slow 55-bar
lookback is also worse despite trading less. Nothing was changed as
a result of the sweep.

## Spec decisions / ambiguities

1. **OBV starts at 0 on the first bar of the frame.** The spec
   fixes OBV[0] = 0; the cumulative level therefore depends on the
   window start, but only 20-bar rolling extremes are traded, so
   the start-date dependence washes out after the first 20 bars.
2. **Breakout levels exclude the current bar.** Implemented as
   `rolling(20).max().shift(1)`, mirroring the Donchian channel in
   this batch: the OBV extreme is built from bars i-20..i-1.
3. **Transition is judged against the prior bar's own levels.**
   Long entry requires OBV[i] > high[i] AND OBV[i-1] <= high[i-1].
4. **Exits are level conditions, not transitions.** Long exit is
   true on any bar OBV sits below its prior-20-bar low; the harness
   exits on the first such bar, so the distinction from a
   transition-only exit does not change backtest results.
5. **Equal closes contribute zero volume.** Per Granville's rule,
   an unchanged close leaves OBV unchanged (verified in tests).

## What the exits actually did

Shipped run (909 trades): 816 trades ended on the harness stop /
trail and only 93 on the OBV signal exit. OBV breakouts fire often
(roughly once per 20 bars per coin) but price rarely runs far enough
for the opposite OBV extreme to exit first — positions live or die
on the 2xATR stop, and the $6,844.59 fee bill on 909 trades is
larger than the $1,847.30 net loss.

No bug fixes requiring re-runs, no PnL-selected tuning.
