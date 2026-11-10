# Polarized Fractal Efficiency

Hans Hannula's Polarized Fractal Efficiency (PFE, TASC January 1994):
the ratio of the direct 10-bar straight-line distance to the summed
single-bar path distance, signed by the 10-bar price move and smoothed
with a 5-bar EMA. Bounded to [−100, +100]: near 0 means chop (the path
is much longer than the straight line), +100 a clean up-move, −100 a
clean down-move.

## Rules

- Long: PFE crosses above 0 AND the minimum PFE over the last 20 bars was below −30 (buy the reversal from a minimum back toward zero). Exit on PFE crossing below +50 after having exceeded +50 since entry (peak-reached exit) OR PFE crossing below 0.
- Short: PFE crosses below 0 AND the maximum PFE over the last 20 bars was above +30. Exit on PFE crossing above −50 after having been below −50 since entry OR PFE crossing above 0.
- Peak tracking is a causal stateful scan over the signal frame (see CALIBRATION.md for the one-bar approximation vs the fill bar).
- All computation is causal, so signals on bar i use only data through bar i's close. ATR stop / trail from the risk layer also applies.

## Source

- Hans Hannula, "Polarized Fractal Efficiency", Technical Analysis of Stocks & Commodities, January 1994
- Investopedia — Polarized Fractal Efficiency: https://www.investopedia.com/terms/p/pfe.asp
- Wickra indicator reference: https://docs.wickra.org/Indicators/Indicator-PolarizedFractalEfficiency

Paper only, no live execution.
