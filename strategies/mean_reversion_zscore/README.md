# Mean Reversion Z-Score

Z-score mean reversion: z = (close - SMA(20)) / std(20) of close. Price stretched far from its 20-bar mean tends to revert; the trade enters only once the stretch starts unwinding, and a 50-bar SMA slope guard keeps the fade out of strong trends.

## Rules

- Long: z crosses back above -2 after being below -2, and SMA(50) slope is flat-to-up (SMA(50) >= SMA(50) 10 bars ago).
- Short: z crosses back below +2 after being above +2, and SMA(50) slope is flat-to-down (SMA(50) <= SMA(50) 10 bars ago).
- Exit: z crosses 0 (price back to the mean), plus ATR stop / trail.

## Source

- Mean reversion trading (Velotrade): https://velotrade.com/blog/mean-reversion-trading

Paper only, no live execution.
