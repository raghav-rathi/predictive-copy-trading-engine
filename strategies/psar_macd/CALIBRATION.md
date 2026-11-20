# Parabolic SAR + MACD Agreement — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is. The sweep
below was run after the fact for reporting only; no alternate was
adopted.

| Parameter | Value | A priori rationale |
|---|---|---|
| PSAR step / max AF | 0.02 / 0.20 | The canonical Wilder defaults. |
| MACD | fast 12, slow 26, signal 9 | The canonical MACD defaults (Gerald Appel). |
| Entry | PSAR flip AND MACD line on the agreeing side of its signal on the same bar | The spec's flip + agreement: the flip alone is not enough, the MACD line must already agree. |
| Exit | Opposite PSAR flip OR MACD line cross against | The spec's exit: either leg breaking ends the trade. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 40 | PSAR is defined from bar 0, MACD needs ~34 bars; 40 gives margin. |

## Sweep (2 alternates, run and reported honestly)

Window and risk layer identical to the shipped run; only the PSAR
step / max AF change.

| Setting | Trades | Win% | Net $ | PF | Fees $ |
|---|---|---|---|---|---|
| Shipped 0.02 / 0.20 | 674 | 35.8% | -2405.90 | 0.92 | 5156.56 |
| Alt A 0.01 / 0.10 | 597 | 36.2% | -2133.73 | 0.92 | 4604.06 |
| Alt B 0.04 / 0.30 | 678 | 35.4% | -3612.58 | 0.87 | 5056.68 |

Per-coin net for Alt A: BTC -849, ETH -2347, HYPE +1063. For Alt B:
BTC -3978, ETH -1355, HYPE +1720. All three settings lose
combined; the slower PSAR (Alt A) loses least but still ends
negative on every coin except HYPE, and the differences are within
noise for a 600-trade sample. Shipped config stands as specified.

## Spec decisions / ambiguities

1. **PSAR seed.** Seeded LONG from bar 0 only (SAR = low[0],
   EP = high[0], AF = 0.02). The first two closes are never used to
   seed bar 0 — a falling first bar flips the PSAR to short at
   bar 1, as the unit test asserts. This is the spec's explicit
   seeding rule, not the common "seed from the first two closes"
   shortcut.
2. **Flip reset.** On a flip the SAR resets to the prior extreme
   point (EP), per Wilder. The flip is tested on the close vs the
   SAR computed for that bar (after the two-bar clamp), using only
   data through bar i's close.
3. **Two-bar clamp.** The SAR is clamped against the prior two
   bars' lows (long) / highs (short), per Wilder. On a flat frame
   the SAR pins at the flat low and never moves.
4. **MACD agreement is line vs signal, not histogram.** The entry
   requires the MACD line above (long) / below (short) its signal
   on the flip bar; the exit uses the line crossing its signal.
   The histogram is computed for diagnostics only.
5. **A flip without MACD agreement is not an entry — but it is an
   exit.** The reversal-frame test shows a flip back to long at
   bar 73 with the MACD line still below its signal: no long
   entry fires, while a short position would exit on that flip.

## What the exits actually did

Shipped run (674 trades): 449 trades ended on the harness stop /
trail and 225 on a signal exit. Stops dominate on all three coins
(BTC 140/210, ETH 156/217, HYPE 153/247) — the PSAR flip is slow
to confirm the reversal, so the 2xATR stop usually ends the trade
first. HYPE's 41.7% win rate with PF 1.25 is the only bright
spot and rests on a single coin in a single window.

No bug fixes requiring re-runs, no PnL-selected tuning.
