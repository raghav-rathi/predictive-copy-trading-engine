# Chande Momentum Oscillator — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a
priori from the spec, and the backtest numbers were reported as-is.
Two alternates were run after the fact as a robustness check only;
neither was adopted.

| Parameter | Value | A priori rationale |
|---|---|---|
| CMO window | 14 bars | Spec-assigned; Chande's common 9–20 range, 14 is the mid textbook setting. |
| CMO formula | 100*(Su - Sd)/(Su + Sd), zero denominator -> 0 | Chande (1994); raw sums of up/down close moves, not Wilder-smoothed. |
| Thresholds | -50 / +50 | Chande's conventional overbought/oversold levels. |
| Long entry | CMO crosses up through -50 (transition only) | Spec: re-emerging from oversold. |
| Short entry | CMO crosses down through +50 (transition only) | Spec: falling out of overbought. |
| Exit | opposite cross only (plus harness stop/trail) | Spec's exit; a cross through the far threshold closes the trade. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 40 | CMO needs 14 bars (first valid at bar 14); 40 gives margin. |

## Sweep results (same window, local cache only)

| Config | Trades | Net $ | PF | Fees $ |
|---|---|---|---|---|
| **Shipped CMO14** | **587** | **-5753.29** | **0.80** | **4307.90** |
| Alt-A CMO9 | 1120 | -8223.37 | 0.81 | 7173.75 |
| Alt-B CMO20 | 325 | -3888.37 | 0.77 | 2340.75 |

Per-coin, Alt-A: BTC -4228.34, ETH -3054.29, HYPE -940.73.
Per-coin, Alt-B: BTC -2471.86, ETH +287.99, HYPE -1704.50.
Both alternates lose money. Alt-B loses less in dollars but has a
worse profit factor (0.77 vs 0.80) and still loses on two of three
coins — a slower oscillator trades less and bleeds slower, not an
edge. Nothing was changed as a result of the sweep.

## Spec decisions / ambiguities

1. **Zero-denominator guard:** a flat 14-bar window (Su = Sd = 0)
   yields CMO = 0, as assigned. The first valid CMO is at bar 14,
   not bar 13, because the first close-to-close move needs bar 1.
2. **Crosses are strict:** long entry needs CMO > -50 with the prior
   bar <= -50; sitting exactly on -50 does not fire.
3. **Exit is the opposite cross.** There is no zero-line exit and no
   exit on re-entering the extreme; the harness stop/trail does most
   of the exiting here (475 of 587 exits).

## What the exits actually did

Shipped run (587 trades): 475 trades ended on the harness stop /
trail and only 112 on the opposite CMO cross. Entries fire ~1 trade
per 10 bars per coin, and the position then rides until the stop or
the opposite cross — mean-reversion entries against 1h momentum do
not pay on this window.

No bug fixes requiring re-runs, no PnL-selected tuning.
