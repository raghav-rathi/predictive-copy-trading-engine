# Dual Momentum — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Absolute-momentum lookback | 240 bars (~10 days) | Antonacci's published lookback is 12 months. On 1h bars a literal 12-bar lookback is noise; 240 bars (~10 days) is the 1h adaptation chosen a priori per the spec — the shortest window that still measures a trend rather than a wiggle. |
| Relative momentum | Coin 240-bar log return minus mean of the three coins' 240-bar log returns | Antonacci's relative-strength leg, equal-weighted across the three-coin basket (no cash/bond leg exists in this universe). |
| Basket close | Geometric mean of the three closes | Informational only; the trading logic uses the log-return basket, not the basket level. |
| Rank | 1 = highest rel_mom, 3 = lowest; ties broken by coin order (BTC, ETH, HYPE) | Deterministic ranking; ties are measure-zero on continuous returns. |
| Entry | Top-ranked + abs_mom > 0 long; bottom-ranked + abs_mom < 0 short; entry on first qualifying bar | Antonacci verbatim: hold the relative winner only while its absolute momentum is positive, else be flat (here: short the relative loser while its absolute momentum is negative, the symmetric short leg the spec requires). |
| Exit | Rank flip or absolute momentum turning against the position | Per spec: exit = rank flip or absolute momentum turning negative/positive against the position. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 300 | 240-bar lookback + margin for the basket to stabilise. |

## Spec deviations

1. **240-bar lookback instead of 12 bars / 12 months.** The spec
   explicitly forbids a 12-bar 1h lookback and directs the 240-bar
   (~10-day) adaptation of Antonacci's 12-month lookback. This is
   a timescale translation, not a PnL-tuned choice.
2. **No cash leg.** Antonacci rotates to bonds when no asset has
   positive absolute momentum. There is no bond leg in this
   three-coin universe, so the system is flat instead — and, per
   the spec, shorts the bottom-ranked coin when its absolute
   momentum is negative.
3. **Per-coin books, not one winner.** Antonacci holds a single
   winner. This batch's harness runs one book per coin, so the
   system can be long the top coin and short the bottom coin
   simultaneously. The ranking logic itself is unchanged.
4. **Basket alignment.** HYPE is missing 2 bars vs BTC/ETH in the
   window. Basket columns are computed on the union of timestamps
   with closes forward-filled across missing bars; each coin is
   backtested on its own bars only.

No bug fixes requiring re-runs, no PnL-selected tuning.
