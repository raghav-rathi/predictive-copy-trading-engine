# Bollinger MACD

Bollinger(20, 2.0) band tag + MACD(12,26,9) cross: a
mean-reversion bounce with a momentum trigger — only buy the
lower-band tag once MACD momentum actually turns up.

## Rules

- **Long entry:** MACD line crosses above its signal line on this
  bar AND the low touched or pierced the lower Bollinger band
  within the last 3 bars (min low of bars i-2..i <= the current
  bar's lower band).
- **Short entry:** MACD crosses below its signal line AND the high
  touched or pierced the upper band within the last 3 bars
  (max high of bars i-2..i >= the current bar's upper band).
- **Long exit:** MACD crosses below its signal line OR close above
  the upper band (reached the opposite band).
- **Short exit:** MACD crosses above its signal line OR close
  below the lower band.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

Bollinger is `strategies/base.py: bollinger`, MACD is
`strategies/base.py: macd`, crosses are `crossed_above` /
`crossed_below`. The band-touch window uses the current bar's
band value with the trailing 3-bar low/high window; the band
value itself uses data through bar i only, so there is no
lookahead. All computation is causal, so signals on bar i use
only data through bar i's close.

## Source

- https://www.stocks365.com/blog/bollinger-bands-macd-ultimate-combo-strategy-1139
- https://signal2forex.com/2019/09/06/bollinger-bands-and-macd-strategy/

Paper only, no live execution.
