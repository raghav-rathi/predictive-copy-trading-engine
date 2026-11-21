# Ehlers Center of Gravity — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a
priori from the spec, and the backtest numbers were reported as-is.
Two alternates were run after the fact as a robustness check only;
neither was adopted.

| Parameter | Value | A priori rationale |
|---|---|---|
| CG window | 10 bars of closes | Spec as written (Ehlers' standard CG length). |
| CG formula | CG = -sum((i+1)*p[i] for i in 0..9) / sum(p[i]), p[0] oldest | Spec as written; see the convention note below. |
| Trigger | SMA(3) of CG | Spec as written. |
| Entry | CG crosses trigger (transition only) | The spec's trigger. |
| Exit | opposite cross (plus harness stop/trail) | The spec's exit. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 40 | CG needs 10 bars; trigger needs 3 CG values (first at bar 11); 40 gives margin. |

## Sweep results (same window, local cache only)

| Config | Trades | Net $ | PF | Fees $ |
|---|---|---|---|---|
| **Shipped CG10 / trigger SMA3** | **3657** | **-20893.09** | **0.70** | **18528.97** |
| Alt-A CG20 / trigger SMA5 | 1886 | -11663.90 | 0.78 | 11691.12 |
| Alt-B CG5 / trigger SMA2 | 6666 | -25631.02 | 0.63 | 20757.23 |

Per-coin, Alt-A: BTC -5273.15, ETH -4440.50, HYPE -1950.24.
Per-coin, Alt-B: BTC -9528.88, ETH -9208.65, HYPE -6893.49.
Lengthening the window (Alt-A) halves the trade count and halves the
loss but still loses on every coin; shortening it (Alt-B) nearly
doubles the churn and loses more. The loss scales with trade count,
which is the signature of a fee-driven churn loser, not a parameter
problem. Nothing was changed as a result of the sweep.

## Spec decisions / ambiguities

1. **Weight/sign convention — implemented exactly as specified in
   the brief, and it is the REVERSE of Ehlers' original.** The brief
   defines p[0] as the oldest price with weight (i+1), so the most
   recent price gets weight 10 and the oldest weight 1, with an
   overall negative sign. Ehlers' original paper ("The CG
   Oscillator", Mesa Software) counts position from the most recent
   price (weight 1) to the oldest (weight 10) and inverts the sign
   so the oscillator moves in phase with price. With the brief's
   convention CG moves OPPOSITE to price: rising prices push CG
   down, falling prices push it up. A "long on cross up" entry is
   therefore triggered by falling prices. This was implemented as
   specified, not "corrected" — flipping the weights would be a
   different strategy and was not run.
2. **Price input is the close.** The brief says "prices p[0..9]";
   the close is used. Ehlers' EasyLanguage code uses the close by
   default as well.
3. **No +(Length+1)/2 centering term.** Some platform
   implementations (e.g. cTrader) add (Length+1)/2 so CG oscillates
   about zero. The brief's formula has no centering term, so CG sits
   near -5.5 on flat prices; only CG-vs-trigger crosses are traded,
   so the offset is irrelevant to the signals.
4. **Cross uses strict inequality on the current bar and
   non-strict on the previous bar** (cg > trigger and prev cg <=
   prev trigger), matching the template's crossed_above semantics.

## What the exits actually did

Shipped run (3657 trades): 2742 trades ended on the opposite-cross
signal and 915 on the harness stop/trail. Positions last only a few
bars on average — CG whipsaws across its 3-bar trigger constantly
at 1h frequency, so the strategy is almost always in the market and
pays fees on every whipsaw.

No bug fixes requiring re-runs, no PnL-selected tuning.
