# Stochastic + Bollinger %b

John Bollinger's %b with Stochastic timing: %b tells you *where*
price sits inside its Bollinger Bands (0 at the lower band, 1 at
the upper band), and the Stochastic cross tells you *when*
momentum turns. The entry waits for both to agree at an extreme.

## Rule (long)

```
%K crosses above %D (transition)
AND %b < 0.2  (price near the lower Bollinger Band)
AND %K < 30   (oversold)
```

- **Exit long:** %b > 0.8 (price reached the upper band — the
  reversion is complete) OR %K crosses below %D (momentum
  rolled over).
- **Short mirror:** %K crosses below %D while %b > 0.8 and
  %K > 70; exit short on %b < 0.2 or %K crossing above %D.
- **Entries are transition-only:** the cross must happen on
  the entry bar; a held position never re-enters. An opposite
  entry condition while in a position flips it.

## This is a mean-reversion-into-band setup, NOT a band-breakout system

Entries are taken *at* the lower/upper band expecting a return
toward the mid-band, and exits are taken *at* the opposite band.
Nothing here trades a band break: a close outside the bands
with no Stochastic cross is not a signal, and a cross in the
middle of the bands (%b between 0.2 and 0.8) is not a signal
either. In a strong trend %b can pin near 0 or 1 for many bars
while %K stays oversold/overbought — the cross requirement is
the only thing that keeps the system from buying every bar of
a downtrend, and the backtest shows it is not enough (see
BACKTEST.md).

## The double-oversold gate

%b < 0.2 + %K < 30 is a double-oversold gate: price must be at
the band *and* momentum must be washed out. Either condition
alone fires far more often (a %K cross below 30 happens on
most pullbacks; %b < 0.2 happens on any drift to the lower
band). Requiring both is what makes the setup selective — 261
to 294 trades per coin over eight months, roughly one a day,
rather than several a day.

## 1h scaling (documented)

- Bollinger(20, 2) and Stochastic(14, 3, 3) are the textbook
  parameters, used as published; nothing is rescaled for 1h.
- %b and %K/%D are seeded deterministically where their
  windows are not yet full (%b to 0.5, %K/%D to 50.0 — the
  neutral values); a seeded 50/50 cannot produce a cross, so
  no signal can fire on seeded data. See indicators.py.

## Honest flags

- Mean reversion into the band assumes price returns to the
  mid-band. In the Mar–Nov 2026 window all three coins spent
  long stretches trending down; buying the lower band into a
  downtrend is exactly how this system loses (see BACKTEST.md:
  combined -$7,816, Sharpe negative on all three coins).
- The %K < 30 / %b < 0.2 gates do not distinguish a washout
  low from the start of a leg down. No trend filter is applied
  by design (the published setup has none); adding one would
  be a different strategy.

## Risk

2×ATR(14) harness stop (the signal-level exit is the real
exit), no trail, no target (the opposite band is the target,
enforced in signals.py), 120-bar (~5-day) max hold, 1% risk
per trade, 3× leverage cap. WARMUP = 40 bars.

Source: John Bollinger, *Bollinger on Bollinger Bands* (2001),
%b chapter (https://www.bollingerbands.com/).
