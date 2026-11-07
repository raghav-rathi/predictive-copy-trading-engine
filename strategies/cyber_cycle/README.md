# Cyber Cycle

John Ehlers' Cyber Cycle (Cybernetic Analysis for Stocks and Futures, ch. 4, 2004). Smoothed price `smooth = (c + 2c1 + 2c2 + c3)/6` is fed through a band-pass cycle filter with alpha = 0.07, then smoothed again into a Signal line with alpha2 = 0.1. The cycle extracts the dominant oscillatory component of price; the Signal line's turns mark cycle tops and bottoms.

## Rules

- Long: Signal crosses above its own 1-bar-delayed value (Signal[i] > Signal[i-1] and Signal[i-1] <= Signal[i-2]).
- Short: Signal crosses below its own 1-bar-delayed value.
- Exit: reverse cross, plus ATR stop / trail. Signals use only data through bar i's close — no lookahead.

## Source

- Ehlers Cyber Cycle, Cybernetic Analysis for Stocks and Futures ch. 4 (2004): https://www.luxalgo.com/library/concept/cyber-cycle/

Paper only, no live execution.
