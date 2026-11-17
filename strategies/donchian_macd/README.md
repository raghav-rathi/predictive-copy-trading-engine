# Donchian MACD

Donchian(20) channel breakout confirmed by MACD(12,26,9): only
trade a 20-bar breakout when momentum agrees with it — histogram
positive for longs, negative for shorts.

## Rules

- **Long entry:** close breaks above the trailing 20-bar high AND
  MACD histogram > 0.
- **Short entry:** close breaks below the trailing 20-bar low AND
  MACD histogram < 0.
- **Long exit:** close below the trailing 20-bar low OR MACD
  histogram flips negative.
- **Short exit:** close above the trailing 20-bar high OR MACD
  histogram flips positive.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

The trailing 20-bar high/low are the extremes of the previous 20
bars (excluding the current bar): a close can only break above a
high that does not already contain the current bar. MACD is the
standard EMA(12) − EMA(26) with a 9-period signal line
(`strategies/base.py: macd`). All computation is causal, so
signals on bar i use only data through bar i's close.

## Source

- Donchian channel breakout + MACD confirmation, per the
  batch-38 spec (no external source supplied).

Paper only, no live execution.
