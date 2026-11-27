# Multi-Timeframe MACD Confirmation

Elder Triple Screen applied to Bitcoin-style crypto perps: trade
the fast timeframe only in the direction of the slow timeframe's
trend. The 1h MACD(12, 26, 9) signal-line cross is the trigger;
the 4h MACD histogram is the trend filter.

- **Long:** 1h MACD line crosses ABOVE its signal line AND the
  4h MACD histogram > 0
- **Short:** 1h MACD line crosses BELOW its signal line AND the
  4h MACD histogram < 0
- **Long exit:** 1h MACD line crosses back BELOW its signal line
  OR the 4h MACD histogram crosses below 0 (or the opposite
  entry fires)
- **Short exit:** mirror
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 168-bar max
  hold (one week), 1% risk/trade, 3x leverage

Entries are CROSS-based, never level conditions: a cross fires
once, so the strategy cannot re-enter every bar while the
condition holds. The 4h MACD is computed on UTC-aligned 4h
bars and mapped onto the 1h grid using only COMPLETED 4h bars
(`strategies.timeframes.macd_4h_aligned`), so there is no
lookahead; the 4h histogram is NaN until ~34 completed 4h bars
(~136 1h bars), and no entry can fire before then.

Parameters: MACD(12, 26, 9) on both timeframes (the canonical
settings from the source). No deviations from the source
mechanism: the source's higher-timeframe filter is the weekly
trend on daily bars; here it is the 4h trend on 1h bars, the
same Triple Screen principle at intraday resolution, because
the backtest grid is 1h.

Sources: Quantpedia, "How to Design a Simple Multi-Timeframe
Trend Strategy on Bitcoin" --
https://quantpedia.com/how-to-design-a-simple-multi-timeframe-trend-strategy-on-bitcoin/
(Elder Triple Screen principle).

Usage:

```python
from strategies.mtf_macd_confirmation import indicators, signals, risk

df = indicators.add_indicators(df)
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-27 Hyperliquid 1h
(BTC/ETH/HYPE, batch-48 pinned window) results and
CALIBRATION.md for the MACD-parameter sensitivity check.
