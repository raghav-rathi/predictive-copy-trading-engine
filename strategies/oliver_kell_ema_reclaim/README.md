# Oliver Kell 20-EMA Reclaim

Oliver Kell's pullback-to-the-20-EMA setup, from his 2020 U.S.
Investing Championship win (+941% in one year), as documented by
Backtest Lab ("He Made 941% in One Year") and the American
Compound write-up. Kell buys leaders — stocks making new highs
after a "wedge pop" — on the pullback to the 20 EMA.

## Mechanism

LONG entry — all of these, on the bar the close crosses back
above the 20 EMA:

- **Leader filter:** close above a RISING 200 SMA, with the 10
  and 20 EMAs also rising.
- **Pullback:** the trailing-20-bar low sits 5–19% below the
  trailing-20-bar high, and the close dipped below the 20 EMA
  at least once in the prior 10 bars.
- **Quiet volume:** the entry bar's volume is below its 20-bar
  average.

SHORT entry is the mirror: close below a FALLING 200 SMA, 10/20
EMAs falling, 5–19% pullback off the trailing-20-bar low, a
close above the 20 EMA within the prior 10 bars, quiet volume,
and the cross back below the 20 EMA.

Daily periods from the source map directly to 1h periods
(10/20/200 bars).

## Exits

- Close back below the 20 EMA (long) / above it (short) — the
  source's exit.
- Hard stop 3% below entry in the source, approximated here by
  the 2xATR(14) harness stop (see CALIBRATION.md).

## Risk

2xATR(14) stop, no trail, no target, 336-bar (~14-day) max
hold, 1% risk per trade, 3x leverage cap. WARMUP = 210 bars.

Sources: Backtest Lab, "He Made 941% in One Year" (Oliver Kell)
(https://www.youtube.com/watch?v=WjcZaEJHlCE); rules also at
https://americancompound.substack.com/p/he-made-941-in-one-year-buying-pullbacks.
