# MACD Histogram

Gerald Appel's MACD (late 1970s), the standard 12/26/9 settings:
the MACD line is EMA(12) − EMA(26) of close, the signal line is
EMA(9) of the MACD line, and the histogram is the MACD line minus
the signal line (the histogram itself was added by Thomas Aspray in
1986). A histogram zero cross is exactly a MACD/signal line cross,
shown as bars: above zero, MACD is pulling away above its signal
(momentum building up); below zero, the reverse.

## Rules

- **Long entry:** the MACD histogram crosses above zero.
- **Short entry:** the MACD histogram crosses below zero.
- **Long exit:** the histogram crosses below zero.
- **Short exit:** the histogram crosses above zero.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies;
  the shipped system uses the harness stop/trail as the exit mechanism
  plus the opposite cross. Max hold 120 bars.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- Gerald Appel, MACD (Moving Average Convergence Divergence), 12/26/9:
  https://www.cmelitegroup.com/knowledge-hub/macd-indicator/

Paper only, no live execution.
