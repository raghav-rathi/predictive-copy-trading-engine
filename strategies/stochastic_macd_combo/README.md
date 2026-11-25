# Stochastic + MACD Combo

Fast Stochastic %K(14)/%D(3) (George C. Lane, StockCharts
ChartSchool) crossed against the MACD(12,26,9) histogram sign:
the Stochastic cross is the trigger, the MACD histogram is the
trend filter, so a cross only trades when MACD agrees with its
direction.

- **Long:** %K crosses above %D while %K < 30 (oversold cross)
  AND MACD histogram > 0
- **Short:** %K crosses below %D while %K > 70 (overbought
  cross) AND MACD histogram < 0
- **Exit:** the opposite Stochastic cross OR the MACD histogram
  flipping sign
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 60-bar max
  hold, 1% risk/trade, 3x leverage (the harness stops sit
  behind the signal logic as a safety net for gap-through
  moves)

Parameters: %K(14), %D = SMA(%K, 3), MACD(12,26,9). A zero
14-bar high-low range (flat bars) reads %K = 50 (neutral).
ATR(14) in the harness for the stop/trail.

Usage:

```python
from strategies.stochastic_macd_combo import indicators, signals, risk

df = indicators.add_indicators(df)  # k_period=14, d_period=3 defaults
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-25 Hyperliquid 1h
(BTC/ETH/HYPE, batch-46 pinned window) results and
CALIBRATION.md for the %K-period 7/14/21 sensitivity check
and the lookahead audit. No parameter was tuned to PnL.

Source: StockCharts ChartSchool, "Stochastic Oscillator (Fast,
Slow, and Full)" —
https://chartschool.stockcharts.com/~gitbook/pdf?page=QVB5cA3WHQlQdjo1YmxN&only=yes&limit=100
(verified via search 2026-11-25; confirms %K = 100 × (close −
lowest low) / (highest high − lowest low) over 14 periods,
%D = 3-period SMA of %K, and the fast/slow/full versions).
MACD(12,26,9) is the standard MACD from `strategies/base.py`.
