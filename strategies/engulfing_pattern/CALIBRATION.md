# Engulfing Pattern — Calibration

Params were fixed a priori per the strategy spec and the source
canon; there was no parameter sweep and none is planned on the
backtest window.

- **Body-engulf definition**: current body fully covers the prior
  body (`c >= o.shift(1)` and `o <= c.shift(1)`, equality counts).
  Strict textbook definition — a partial cover is a hammer/pin
  variant, a different pattern with different statistics.
- **EMA(20) trend filter**: the canonical short-horizon trend read.
  Longs need close > EMA(20), shorts need close < EMA(20) on the
  engulfing bar's own close. Fixed at 20 — the commonly quoted
  length — not tuned.
- **Risk**: 1.5xATR stop / 2xATR trail / 48-bar max hold / 1% risk
  / 3x leverage, the module's standard reversal-trade framing.

**Why no sweep:** the backtest result (see BACKTEST.md) is a clear
loser on all three coins with a deeply negative expectancy
(-$10.14/trade combined). Tuning the EMA length or the engulf
equality tolerance on a window this negative would be
optimizing noise into a flat line — the decision would be
"make it lose less," not "find an edge." If this pattern ever
gets revisited, it needs a structural change first (real swing
structure for location, not a same-timeframe EMA) on
walk-forward data, not a parameter tweak here.
