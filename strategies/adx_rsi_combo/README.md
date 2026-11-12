# ADX + RSI Combo

ADX(14) as the trend-strength filter, RSI(14) as the momentum trigger.
The classic pairing: ADX says whether a trend is worth trading at
all (above 25 = trending, below = range-bound chop), RSI says when to
enter it. A long is taken when RSI crosses back up out of oversold
territory while the trend is confirmed strong; a short is the mirror
image off overbought.

## Rules

- **Long entry:** RSI(14) crosses above 30 AND ADX(14) > 25.
- **Short entry:** RSI(14) crosses below 70 AND ADX(14) > 25.
- **Long exit:** RSI(14) crosses back below 50.
- **Short exit:** RSI(14) crosses back above 50.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- ADX and RSI Trading Strategies (OpoFinance): https://blog.opofinance.com/en/adx-and-rsi-trading-strategies/

Paper only, no live execution.
