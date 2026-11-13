# MACD Signal-Line Crossover

Gerald Appel's MACD (1979): the MACD line is the 12-period EMA of the
close minus the 26-period EMA, and the signal line is a 9-period EMA
of the MACD line. The crossover of the MACD line through its signal
line is the classic momentum trigger — buy when the MACD line crosses
above the signal line, sell (or short) when it crosses below.

## Rules

- **Long entry:** MACD line crosses above its signal line.
- **Short entry:** MACD line crosses below its signal line.
- **Long exit:** MACD line crosses below its signal line (the opposite
  cross).
- **Short exit:** MACD line crosses above its signal line.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies;
  the shipped system uses the harness stop/trail as the exit mechanism
  plus the opposite cross. Max hold 120 bars.
- Parameters are Appel's published defaults (12, 26, 9); nothing was
  tuned to this window.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- Gerald Appel, MACD (1979): https://www.investopedia.com/terms/m/macd.asp

Paper only, no live execution.
