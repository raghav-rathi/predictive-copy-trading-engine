# Ehlers Fisher Transform Trend

John Ehlers' Fisher Transform (Cybernetic Analysis for Stocks
and Futures, 2004) applied as a trend system: normalize the
close inside its trailing 10-bar high/low range, map it to
[-1, 1], Fisher-transform it, smooth once — then trade the
0-cross.

## Rule (long)

```
x    = 2 * (C - min(L,10)) / (max(H,10) - min(L,10)) - 1, clamped to +/-0.999
f_raw = 0.5 * ln((1 + x) / (1 - x))
fisher[i] = 0.5 * f_raw[i] + 0.5 * fisher[i-1]
LONG when fisher crosses above 0 from below AND fisher is rising
```

- **Short mirror:** fisher crosses below 0 from above and is
  falling.
- **Exit long:** fisher crosses back below 0, OR fisher turns
  down two bars in a row. Exit short on the mirror. A cross
  back through 0 flips the position (exit + opposite entry on
  the same bar); a two-bar-turn exit only closes it.
- **Entries are transition-only:** a position opens only on
  the cross bar, never re-entered while already holding.

## What the Fisher Transform is — and is not

The Fisher Transform near-Gaussianizes price: it stretches the
normalized price position so that values near the extremes of
the 10-bar range stand out sharply, while mid-range values
compress toward zero. It is **not a momentum oscillator** —
there is no overbought/oversold reading here, and the usual
oscillator levels (±1, ±2) carry no meaning. The only signal
is the **0-cross**: the normalized price position flipping
from the lower to the upper half of its 10-bar range (and
back). Treat it as a regime flip, not as momentum strength.

## 1h scaling (documented)

- The 10-bar window is Ehlers' own; on 1h bars it is a 10-hour
  range, much shorter than the 10-day range of the daily
  original — so the transform whipsaws far more often.
- Before the first complete 10-bar window, fisher_raw is
  defined as 0.0 (price at mid-range); flat bars (zero 10-bar
  range) also map to x = 0. See indicators.py for the seeding.
- WARMUP = 30 bars covers the window plus the smoothing settle.

## Honest flag: the 0-cross whipsaws on 1h crypto

On 1h crypto the normalized price position oscillates around
mid-range constantly, so the Fisher 0-cross fires hundreds of
times per coin (see BACKTEST.md: ~650 trades per coin in eight
months). Each cross is a full round trip at 0.055% per side in
fees + slippage, and the two-bar-turn exit cuts winners as
readily as losers. The mechanism works exactly as specified —
the losses are the strategy's, not an implementation bug. Do
not "fix" this by lengthening the window or adding a filter
without treating that as a new, separately validated strategy.

## Risk

2×ATR(14) harness stop as a backstop (the signal-level cross
and two-bar-turn exits are the real exits), no trail, no
target, 120-bar (~5-day) max hold, 1% risk per trade, 3×
leverage cap. WARMUP = 30 bars.

Source: John Ehlers, "The Fisher Transform"
(https://www.mesasoftware.com/papers/TheFisherTransform.pdf).
