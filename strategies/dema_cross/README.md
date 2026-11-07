# DEMA Crossover

Patrick Mulloy's Double Exponential Moving Average (Technical Analysis of Stocks & Commodities, 1994). DEMA(n) = 2*EMA(n) − EMA(EMA(n)): the second EMA term cancels much of the lag of a plain EMA while keeping the smoothing. The fast DEMA(12) reacts to trend changes sooner than the slow DEMA(26), so their crossover marks trend turns with less delay than a classic EMA crossover.

## Rules

- Long: fast DEMA(12) crosses above slow DEMA(26).
- Short: fast DEMA(12) crosses below slow DEMA(26).
- Exit: reverse cross, plus ATR stop / trail. Signals use only data through bar i's close — no lookahead.

## Source

- Patrick Mulloy DEMA (1994): https://www.tickatlas.com/learn/indicators/dema

Paper only, no live execution.
