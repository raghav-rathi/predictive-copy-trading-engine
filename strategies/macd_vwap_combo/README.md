# MACD + Session VWAP

Gerald Appel's MACD(12, 26, 9) cross entries, filtered by the
session (UTC-day) VWAP regime: only take a bullish MACD cross when
price is above the day's VWAP (buyers in control intraday), and only
take a bearish cross when price is below it.

## Rules

- **MACD:** EMA(12) − EMA(26); signal line EMA(9) of the MACD line.
- **Session VWAP:** typical price weighted by volume, accumulated
  within each UTC day and reset at UTC midnight.
- **Long entry:** MACD line crosses above its signal line while
  close > session VWAP.
- **Short entry:** MACD line crosses below its signal line while
  close < session VWAP.
- **Long exit:** MACD line crosses below its signal line.
- **Short exit:** MACD line crosses above its signal line.
- ATR stop / trail from the risk layer also applies; max hold 120 bars.

The VWAP gates entries only, never exits.

All computation is causal, so signals on bar i use only data through
bar i's close. On 1h crypto bars a "session" is a UTC calendar day
(24 bars).

## Source

- Gerald Appel, MACD: https://www.investopedia.com/terms/m/macd.asp
- VWAP: https://www.investopedia.com/terms/v/vwap.asp

Paper only, no live execution.
