# ADX EMA Trend

EMA(20)/EMA(50) crossover with an ADX(14) trend-strength filter:
only take a crossover when the trend is actually strong, and only
in the direction the directional indicators agree with.

## Rules

- **Long entry:** EMA(20) crosses above EMA(50) AND ADX > 25 AND
  +DI > -DI at the cross.
- **Short entry:** EMA(20) crosses below EMA(50) AND ADX > 25 AND
  -DI > +DI at the cross.
- **Long exit:** EMA(20) crosses below EMA(50) OR ADX < 20.
- **Short exit:** EMA(20) crosses above EMA(50) OR ADX < 20.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

ADX, +DI and -DI use standard Wilder smoothing (see
`strategies/base.py: adx`); EMA is the standard exponential
average. All computation is causal, so signals on bar i use only
data through bar i's close. ADX > 25 is the conventional
"trending" threshold and ADX < 20 the conventional "no trend"
threshold; both are taken from the sources, not tuned.

## Source

- EMA crossover swing strategy, Trading Compendium:
  https://tradingcompendium.com/en/trading-strategies/ema-crossover-swing-strategy
- EMA crossover and ADX, ForexBite:
  https://www.forexbite.com/strategies/ema-crossover-and-adx/

Paper only, no live execution.
