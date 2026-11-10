# Chande Dynamic Momentum Index

Tushar Chande & Stanley Kroll's Dynamic Momentum Index (DMI) — a
variable-length RSI from *The New Technical Trader* (1994). The
lookback adapts to relative volatility: when the market is more
volatile than its own recent average the RSI shortens (down to 5
bars) to react faster; when it is quieter than average it lengthens
(up to 30 bars) to smooth out noise. TD = clamp(round(14 / Vi), 5,
30), where Vi = stddev(close, 5) / SMA(stddev(close, 5), 10).

**Note:** this DMI is Chande's Dynamic Momentum Index, NOT Wilder's
Directional Movement Index — same abbreviation, different indicator.

## Rules

- Long: DMI crosses up through 30. Exit on DMI crossing above 70.
- Short: DMI crosses down through 70. Exit on DMI crossing below 30.
- DMI is computed with simple means of close-to-close gains/losses
  over the last TD bars (not Wilder smoothing); 50 when there are no
  gains or losses.
- All computation is causal, so signals on bar i use only data
  through bar i's close. ATR stop / trail from the risk layer also
  applies.

## Source

- Tushar Chande & Stanley Kroll, *The New Technical Trader*, John Wiley & Sons (1994)
- Formula reference (Wickra): https://docs.wickra.org/Indicators/Indicator-DynamicMomentumIndex
- Concept reference (LuxAlgo): https://www.luxalgo.com/library/concept/dynamic-momentum-index/

Paper only, no live execution.
