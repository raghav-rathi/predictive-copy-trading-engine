# Time Segmented Volume

Worden Brothers' Time Segmented Volume (TSV): per-bar signed money flow = (close − close[1]) × volume, summed over a rolling 18-bar window (Worden's default). Unlike OBV, which adds or subtracts the full volume by direction only, TSV weights volume by the size of the close-to-close move, so large moves count more. Positive TSV = net accumulation over the window; negative TSV = net distribution. The zero line is the baseline.

## Rules

- Long: TSV(18) crosses above zero. Exit on TSV crossing back below zero (the opposite cross).
- Short: TSV(18) crosses below zero. Exit on TSV crossing back above zero.
- TSV on bar i uses only closes and volumes through bar i, so signals on bar i use no future data. ATR stop / trail from the risk layer also applies.
- Note: Worden's published rules pair TSV with a 9-bar EMA of itself as the signal line; this strategy uses the zero-line cross only, exactly as briefed.

## Source

- Wickra docs — Time Segmented Volume (TSV) (formula, Worden's default 18, warmup period + 1): https://docs.wickra.org/Indicators/Indicator-Tsv
- Supermoney — Time Segmented Volume: Definition, Calculation, and Applications: https://www.supermoney.com/encyclopedia/time-segmented-volume
- Coinpedia — Time Segmented Volume: A Must-Have Tool for Crypto Trading: https://coinpedia.org/traders/what-is-time-segmented-volume/

Paper only, no live execution.
