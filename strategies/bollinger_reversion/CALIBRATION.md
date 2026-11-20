# Bollinger Bands %b Mean Reversion — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a
priori from the spec, and the backtest numbers were reported as-is.
A small two-alternate sweep was run after the fact and is reported
honestly below; the shipped config was NOT changed on its basis.

| Parameter | Value | A priori rationale |
|---|---|---|
| Bollinger Bands | (20, 2.0) | The canonical Bollinger construction: SMA(20) middle, +/- 2 sample standard deviations. |
| Entry | close < lower band (long) / close > upper band (short) | The spec: the band tag IS the signal; %b <= 0 / >= 1. No extra filter. |
| Exit | close back at/above the middle band (long) / at/below it (short) | The spec: reversion to the mean, the SMA(20). |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 40 | Bands need 20 bars; 40 gives margin. |

## Sweep (2 alternates, run after the shipped backtest)

Combined across BTC/ETH/HYPE, same window and risk layer:

| Config | Trades | Win% | Net $ | Profit factor | Fees $ |
|---|---|---|---|---|---|
| **Shipped (20, 2.0)** | **1104** | **41.9%** | **-17011.55** | **0.58** | **5952.73** |
| Alt (20, 1.5) | 1755 | 41.9% | -24082.10 | 0.50 | 6859.07 |
| Alt (10, 2.0) | 1089 | 53.1% | -11590.42 | 0.67 | 7306.89 |

Narrower bands (1.5x) fire far more often and lose more; a
faster (10, 2.0) band lifts the win rate to 53.1% but still loses
-$11,590 — the edge is not in the band parameters. The (10, 2.0)
variant was NOT adopted: picking it on this window would be
PnL-tuning a still-losing configuration.

## Spec decisions / ambiguities

1. **Close vs wick for the tag.** The entry uses the close vs the
   band, not the high/low wick. A wick through the band without a
   close beyond it does not enter.
2. **Entry is level-based, not edge-based.** Every bar closing
   outside the band is an entry signal (the harness takes the
   first, since it holds one position at a time). A tag that
   persists for several bars does not queue multiple entries.
3. **Exit is also level-based.** A long exits on any bar closing
   at/above the middle band — including bars before any entry
   (harmless: the harness only acts on the exit when in a
   position).
4. **Bands use the sample standard deviation** (pandas rolling
   std, ddof=1), the standard Bollinger construction.
5. **%b is undefined while the band width is 0** (flat prices):
   it is NaN, and no signal fires on those bars.

## What the exits actually did

Shipped run (1,104 trades): 636 trades ended on the harness stop
/ trail and 468 on the signal exit (close back to the middle
band). The stop-heavy exit mix is the story of this strategy:
tags keep extending instead of reverting, so the risk layer does
most of the exiting.

No bug fixes requiring re-runs, no PnL-selected tuning.
