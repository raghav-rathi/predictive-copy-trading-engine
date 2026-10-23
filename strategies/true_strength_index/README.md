# True Strength Index — signal-line cross with zero-territory filter

William Blau's True Strength Index (TSI), introduced in *Stocks &
Commodities* magazine, January 1991.

## Mechanism

1. `m[j] = close[j] - close[j-1]` — raw price momentum.
2. Double-smooth both momentum and absolute momentum:
   `num = EMA(EMA(m, 25), 13)`, `den = EMA(EMA(|m|, 25), 13)`.
3. `TSI = 100 * num / den` — the double smoothing kills the whipsaw a
   single EMA of momentum keeps; the normalization bounds the
   oscillator in [-100, +100] (a flat market maps to 0, not NaN).
4. `signal = EMA(TSI, 7)` — classic signal line.

Trading rules:

- **long_entry** = TSI crosses above signal AND TSI > 0
  (zero-territory filter: only take longs when the momentum regime is
  bullish)
- **short_entry** = TSI crosses below signal AND TSI < 0
- **long_exit** = TSI crosses below signal (raw cross, no filter —
  never hold a position through a confirmed momentum reversal)
- **short_exit** = TSI crosses above signal

Risk: 1.5xATR(14) stop, 2xATR chandelier trail, no fixed target,
120-bar (~5 day) max hold, 1% risk per trade, 3x max leverage,
long + short allowed (the oscillator is symmetric by construction).

The zero-territory filter is the only discretionary addition: a
signal-line cross against the oscillator's territory is a
counter-trend wobble far more often than a genuine regime flip, so
entries require agreement with the prevailing momentum direction.

## Sources

- https://en.wikipedia.org/wiki/True_strength_index
- http://capital.com/en-eu/learn/technical-analysis/tsi-indicator
