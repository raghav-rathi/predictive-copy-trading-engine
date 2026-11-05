# Zero Lag EMA

Zero Lag EMA (John Ehlers & Ric Way, "Zero Lag (Well, Almost)", 2010): the input series is de-lagged before smoothing — de-lagged input = 2 * close - close shifted by lag, where lag = (n - 1) / 2 rounded — then a standard EMA is applied, so the average tracks price turns faster than a plain EMA of the same length.

## Rules

- Long: ZLEMA(20) crosses above ZLEMA(50).
- Short: ZLEMA(20) crosses below ZLEMA(50).
- Exit: opposite cross.
- Plus ATR stop / trail from the batch-standard risk layer.

## Source

- Zero Lag EMA (ZLEMA): https://www.luxalgo.com/library/concept/zlema/

Paper only, no live execution.
