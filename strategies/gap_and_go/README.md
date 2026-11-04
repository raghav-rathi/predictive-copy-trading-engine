# Gap and Go

Gap-and-Go (momentum day-trading setup), adapted to 1h crypto: a bar gaps >=1.5% from the prior close on >=2x average volume; entry when a bar within the next 3 bars closes beyond the gap bar's extreme in the gap direction; exit when price closes back through the gap bar's midpoint (gap fill).

## Rules

- Long: gap-up >=1.5% on >=2x volume, then a close above the gap bar's high within 3 bars.
- Short: gap-down <=-1.5% on >=2x volume, then a close below the gap bar's low within 3 bars.
- Exit: close back through the gap bar's midpoint (plus ATR stop / trail).

## Source

- Gap and Go (momentum day-trading setup): https://www.luxalgo.com/library/concept/gap-and-go/

Paper only, no live execution.
