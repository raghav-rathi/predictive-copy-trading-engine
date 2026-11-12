# Stochastic Momentum Index

William Blau's Stochastic Momentum Index (*Momentum, Direction, and
Divergence*, 1995): where the close sits relative to the midpoint of
the recent 13-bar high/low range, double-smoothed with EMAs (25, 2),
on a -100 to +100 scale. Blau's refinement of the stochastic
oscillator: the midpoint reference and double smoothing cut the false
swings of the classic %K.

## Rules

- **Long entry:** SMI crosses up through -40 (out of the oversold zone).
- **Short entry:** SMI crosses down through +40 (out of the overbought zone).
- **Long exit:** SMI crosses back below 0 (momentum flips to the lower
  half of the range).
- **Short exit:** SMI crosses back above 0.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies;
  the shipped system uses the harness stop/trail as the exit mechanism
  plus the zero-line cross. Max hold 120 bars.
- Parameters are Blau's published defaults (13-bar range, EMA 25/2
  smoothing, +/-40 zones); nothing was tuned to this window.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- William Blau, *Momentum, Direction, and Divergence* (1995): https://www.alphaexcapital.com/stocks/technical-analysis-for-stock-trading/technical-indicators-for-stocks/stochastic-momentum-index

Paper only, no live execution.
