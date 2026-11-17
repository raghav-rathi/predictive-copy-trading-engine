# Heikin Ashi + MACD Momentum Filter

Heikin Ashi candles smooth out the noise of raw candles, and the
MACD histogram on the Heikin Ashi close times the momentum turn:
enter when the histogram crosses zero in the direction the Heikin
Ashi candle is already pointing.

## Rules

- **Heikin Ashi candles:** HA-close = (o + h + l + c) / 4;
  HA-open = (prev HA-open + prev HA-close) / 2, seeded on the first
  bar as (o + c) / 2; HA-high = max(h, HA-open, HA-close);
  HA-low = min(l, HA-open, HA-close).
- **MACD(12, 26, 9)** computed on the HA close.
- **Long entry:** MACD histogram crosses above 0 AND the HA candle
  is bullish (HA close > HA open).
- **Short entry:** MACD histogram crosses below 0 AND the HA candle
  is bearish (HA close < HA open).
- **Long exit:** MACD histogram crosses below 0 (opposite
  zero-cross).
- **Short exit:** MACD histogram crosses above 0 (opposite
  zero-cross).
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

Entry needs the zero-cross and the HA direction to coincide on the
same bar: at a sharp V-reversal the histogram can cross zero on the
pivot bar while the HA candle still points the old way (HA-open
lags one bar), and that bar produces no entry. In noisy, trending
price action the two coincide often. All computation is causal, so
signals on bar i use only data through bar i's close.

## Source

- TradingView, "Heikin Ashi + MACD Momentum Filter" by Raisontgh:
  https://tw.tradingview.com/script/uXNlGkhO-Heikin-Ashi-MACD-Momentum-Filter/

Paper only, no live execution.
