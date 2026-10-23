# Ultimate Oscillator Divergence

Larry Williams' Ultimate Oscillator (UO), traded with Williams' own
three-step divergence method, mechanized. From "The Ultimate Oscillator"
(Technical Analysis of Stocks & Commodities, April 1985).

## The indicator

Williams built UO to fix the false-divergence problem of single-window
momentum oscillators: it blends buying pressure over three lookbacks
(7 / 14 / 28 bars) with 4:2:1 weights.

    prev_c = c.shift(1)
    BP     = c - min(l, prev_c)              # buying pressure
    TR     = max(h, prev_c) - min(l, prev_c) # Williams' true range
    avg7   = sum(BP,7)  / sum(TR,7)
    avg14  = sum(BP,14) / sum(TR,14)
    avg28  = sum(BP,28) / sum(TR,28)
    UO     = 100 * (4*avg7 + 2*avg14 + avg28) / 7

Range 0-100. 0 <= BP <= TR at every bar, so each avg is in [0,1].

## The method (Williams' three steps, mechanized)

**Bullish:** price makes a lower low while UO makes a higher low, with
UO dipping below 30 between the two lows. Enter long when UO crosses
above the highest UO reading recorded between the two lows ("rise above
the divergence high"). Exit when UO crosses above 70.

**Bearish (mirror):** price higher high + UO lower high, UO exceeding 70
during the span. Enter short when UO crosses below the span's lowest UO
reading. Exit when UO crosses below 30.

**No lookahead:** pivots are confirmed only (left=3, right=3 bars) -- a
pivot at bar p is usable on bars >= p+3. The pending setup is
re-evaluated from the latest two confirmed pivots whenever a new pivot
confirms; a non-divergent latest pair cancels the setup.

## Risk

1.5xATR hard stop, 2xATR chandelier trail, no fixed target (exits are
signal-driven), 96-bar max hold, 1% risk per trade, 3x max leverage,
both directions.

## Sources

- https://en.wikipedia.org/wiki/Ultimate_oscillator
- https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/ultimate-oscillator
