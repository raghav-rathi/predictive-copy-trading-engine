# Hull MA Crossover

Hull Moving Average crossover (Alan Hull, 2005): HMA(n) = WMA(2 * WMA(n/2) − WMA(n), sqrt(n)). HMA(16) vs HMA(32) cross: long on fast crossing above slow with the fast HMA slope positive; short on cross below with the slope negative. Exit on the opposite cross.

NOTE: Alan Hull himself warned against HMA crossovers — they reintroduce the lag/whipsaw the HMA was designed to remove. This is a test of the popular retail crossover variant, not Hull's recommended slope method.

## Rules

- Long: HMA(16) crosses above HMA(32) and fast HMA slope is positive.
- Short: HMA(16) crosses below HMA(32) and fast HMA slope is negative.
- Exit: opposite cross (plus ATR stop / trail).

## Source

- Hull Moving Average (Alan Hull): https://capital.com/en-int/learn/technical-analysis/hull-moving-average

Paper only, no live execution.
