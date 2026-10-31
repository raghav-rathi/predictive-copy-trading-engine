# Linear Regression Channel

Raff regression channel traded as mean reversion: price stretched
two residual standard deviations from its own 50-bar trend line is
faded back toward the line.

## Mechanism

Over each trailing 50-bar window, fit OLS of closes against the
bar index (closed form, exactly equivalent to np.polyfit on the
window):

- mid = fitted value at the current bar (the least-squares trend
  line evaluated at the window's end)
- resid_std = population std of (closes − fitted) over the window
- upper = mid + 2 × resid_std
- lower = mid − 2 × resid_std

This differs from the classic Raff construction, where the channel
width is set by the single furthest high/low from the line; here
the width is 2 residual standard deviations, which makes the bands
comparable to Bollinger Bands around a sloped (rather than flat)
centre line. The window uses only closes through the current bar,
so the channel is causal.

## Entry / exit

- **Long entry:** close crosses below the lower band.
- **Short entry:** close crosses above the upper band.
- **Long exit:** close crosses above the midline.
- **Short exit:** close crosses below the midline.
- The risk layer adds a 2xATR stop, a 2.5xATR trail, and a
  120-bar max hold.

## Source

- Raff Regression Channel (Gilbert Raff): least-squares line of
  best fit with evenly spaced lines above and below; trend lines
  act as support/resistance and breaks signal reversal:
  https://www.interactivebrokers.eu/campus/glossary-terms/raff-channel-indicator/
  (verified; the 50-bar window, 2-residual-std width, and
  mean-reversion entry/exit rules are this strategy's own
  construction — the classic width rule uses the furthest
  high/low, not residual std.)

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 55 bars
(50-bar window + margin).

## Honest limitation

Mean reversion into a strong trend is the classic way to bleed:
in a sustained trend the bands slope with price, closes can ride
outside a band for many bars, and each fade adds a stop-out. The
midline exit also caps winners at the trend line by design, so a
genuine reversal that runs past the line is exited early (see
BACKTEST.md).

Paper only, no live execution.
