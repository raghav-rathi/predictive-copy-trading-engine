# Accumulation/Distribution Line — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a
priori from the spec, and the backtest numbers were reported as-is.
Two alternates were run after the fact as a robustness check only;
neither was adopted.

| Parameter | Value | A priori rationale |
|---|---|---|
| Money flow multiplier | ((C-L)-(H-C))/(H-L), H==L -> 0 | Chaikin's definition; close location value in [-1, +1]. |
| Money flow volume | MFM * v | Chaikin's definition. |
| A/D line | cumulative sum of MFV | Chaikin's definition; starts at the first bar's MFV. |
| Signal line | SMA(20) of AD | Spec-assigned; the standard Chaikin-oscillator-era smoothing length. |
| Long entry | AD crosses up through SMA(20) (transition only) | Spec. |
| Short entry | AD crosses down through SMA(20) (transition only) | Spec. |
| Exit | opposite cross only (plus harness stop/trail) | Spec's exit. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 40 | SMA(20) needs 20 bars; 40 gives margin. |

## Sweep results (same window, local cache only)

| Config | Trades | Net $ | PF | Fees $ |
|---|---|---|---|---|
| **Shipped SMA20** | **2304** | **-16976.83** | **0.68** | **12242.78** |
| Alt-A SMA10 | 3401 | -22666.99 | 0.61 | 12726.56 |
| Alt-B SMA30 | 1772 | -11574.46 | 0.76 | 11183.67 |

Per-coin, Alt-A: BTC -8982.31, ETH -8541.77, HYPE -5142.91.
Per-coin, Alt-B: BTC -6279.66, ETH -2877.07, HYPE -2417.74.
Both alternates lose money on all three coins. Alt-B (SMA30) loses
less in dollars and has a better PF (0.76 vs 0.68) because a slower
signal line trades less — but it still loses on every coin, so
slowing the whipsaw down is not an edge, just a slower bleed.
Nothing was changed as a result of the sweep.

## Spec decisions / ambiguities

1. **A/D starts at the first bar's MFV** (cumulative sum from zero
   at the window start). The line has no absolute level, only
   changes matter — which is why the signal is a cross of its own
   SMA rather than a level.
2. **H == L guard:** a zero-range bar contributes MFV = 0 and the
   line carries forward unchanged.
3. **BTC and ETH both printed exactly 801 trades.** Verified genuine,
   not a data mix-up: BTC had 401 long + 401 short entries, ETH 402
   + 402, on different price series (BTC 70,677 -> 60,548; ETH
   2,083.6 -> 1,701.7). The AD/SMA cross fires roughly every 7.5
   bars on both, and because entries strictly alternate long/short,
   nearly every entry becomes a trade — the counts coincide.
4. **Exits are dominated by the signal cross** (1,493 of 2,304),
   not the stop — the system flips position on almost every cross,
   so the max-hold and stop rarely bind.

## What the exits actually did

Shipped run (2,304 trades): 1,493 trades ended on the opposite
cross and 811 on the harness stop / trail. The average holding
period is ~2.6 bars — the strategy is effectively always in the
market, flipping on noise, and pays $12,242.78 in fees to do it.

No bug fixes requiring re-runs, no PnL-selected tuning.
