# Volume-weighted MACD

MACD computed not on raw close but on a volume-weighted price series, so bars traded on heavy volume count more in the momentum read.

## Rules

- Volume-weighted price: p_t = rolling 20-bar sum(close * volume) / rolling 20-bar sum(volume).
- MACD on p_t: fast EMA(12) - slow EMA(26); signal EMA(9) of the MACD line; histogram = MACD - signal.
- Long: MACD line crosses above its signal line AND histogram > 0 AND p_t > SMA(50) of close (prior-bar SMA, to avoid comparing the current close against an indicator computed from itself).
- Short: MACD line crosses below its signal line AND histogram < 0 AND p_t < SMA(50) of close (prior-bar SMA).
- Exit long: MACD crosses below its signal line. Exit short: MACD crosses above its signal line.

## Source

- Volume-weighted MACD (no verified source URL).

Paper only, no live execution.
