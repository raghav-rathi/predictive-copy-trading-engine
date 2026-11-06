# Fractal Dimension Index

Ehlers' Fractal Dimension Index (FDI): a direction-blind measure of how trending vs choppy a market is. A straight-line trend has FDI near 1; a random, choppy market has FDI near 1.5–2.

## Rules

- FDI(30) = (ln(sum of |close-to-close changes| over 30 bars) - ln(highest high - lowest low over 30 bars)) / ln(2), clipped to [1, 2]. Below 1.5 = trending, above 1.5 = ranging/choppy.
- Entry rule (chosen): enter only in the clean-trend regime, FDI < 1.4, when the close crosses SMA(20) in the trade direction — long on a cross above, short on a cross below. The close is compared against the prior bar's SMA(20).
- Exit long: FDI rises above 1.5 OR close falls below SMA(20). Exit short: FDI rises above 1.5 OR close rises above SMA(20).

## Source

- Fractal Dimension Index (Ehlers): https://docs.prorealalgos.com/fractaldimensionindex.html

Paper only, no live execution.
