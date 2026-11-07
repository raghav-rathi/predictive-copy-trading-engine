# Chaikin Oscillator

Marc Chaikin's Chaikin Oscillator. Money Flow Volume: MFV = ((c−l)−(h−c))/(h−l) × v (0 when h == l). Accumulation/Distribution Line: ADL = cumulative MFV. Chaikin Oscillator: CHO = EMA(3, ADL) − EMA(10, ADL).

## Rules

- Long: CHO crosses above zero AND close above SMA(50) → enter.
- Short: CHO crosses below zero AND close below SMA(50) → enter.
- Exit: reverse zero cross (long exits when CHO crosses below zero, short when it crosses above zero), plus the ATR stop / trail from the risk layer.
- Crosses use only data through bar i's close — no lookahead.

## Source

- MarketInOut — Chaikin Oscillator: https://www.marketinout.com/technical-analysis/chaikin-oscillator

Paper only, no live execution.
