# TTM-Style Keltner Squeeze Breakout

Trade volatility expansion, not compression. When the Bollinger
Bands contract inside the Keltner Channels, volatility has
compressed to the point where the next expansion tends to be
directional — the classic TTM Squeeze setup (John Carter,
*Mastering the Trade*).

- **Squeeze ON:** Bollinger Band(20, 2.0) width < Keltner
  Channel (EMA20 ± 1.5 × ATR(10)) width.
- **Breakout:** close outside the Bollinger Band while the
  squeeze was on within the last 3 bars.

The squeeze itself says nothing about direction; the breakout
bar does. Entering on the squeeze alone catches every false
twitch inside the range, so the entry demands a close outside
the band shortly after compression.

## Entries

- **Long:** squeeze was ON at any of bars j−2..j AND close
  crosses above the Bollinger upper band.
- **Short:** exact mirror — squeeze recent AND close crosses
  below the Bollinger lower band.

## Exits

- **long_exit:** close crosses below the Bollinger lower band
  (the opposite band — the expansion has fully reversed).
- **short_exit:** close crosses above the Bollinger upper band.

## Risk

2.0xATR hard stop, 2.5xATR chandelier trail, no fixed target
(the opposite-band cross is the exit), 96-bar (~4-day) max
hold — a genuine volatility expansion resolves within days; a
breakout that stalls for four days was a false release.
1% risk/trade, 3x leverage cap, long/short symmetric.

Parameters: BB(20, 2.0), KC(EMA20, 1.5×ATR10), squeeze lookback
3 bars. All fixed a priori; no optimization. WARMUP=60.

Usage:

```python
from strategies.keltner_squeeze import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the a-priori calibration rationale.

Sources:

- TTM Squeeze (John Carter) — squeeze = Bollinger Bands inside
  Keltner Channels, trade the breakout.
- StockCharts Keltner Channels —
  https://school.stockcharts.com/doku.php?id=technical_indicators:keltner_channels
