# Bollinger %B Band-Tag Reclaim

Trade the Bollinger %B reclaim, not the tag. %B (John Bollinger)
locates price inside its own Bollinger Band: 0 at the lower band,
0.5 at the middle band, 1 at the upper band, outside the bands
beyond 0/1.

- **%B** = (close − lower band) / (upper band − lower band),
  BB(20, 2.0). A zero-width band (20 identical closes) defines
  %B = 0.5 — price sits exactly on the collapsed band.

## Entries

- **Long:** %B crosses back *above 0* from below — price tagged
  the lower band and reclaimed it. Buying the tag itself
  (%B < 0) catches falling knives; the reclaim demands the
  tag first prove itself.
- **Short:** exact mirror — %B crosses back *below 1* from above.

## Exits

- **long_exit:** %B crosses below 0.5 (back to the middle band —
  the mean-reversion leg has run its course).
- **short_exit:** %B crosses above 0.5.

## Risk

1.5xATR hard stop, 2xATR chandelier trail, no fixed target (the
0.5 cross is the exit), 72-bar (~3-day) max hold — a band tag
that hasn't reverted in three days is a trend, not a tag.
1% risk/trade, 3x leverage cap, long/short symmetric.

Parameters: BB(20, 2.0). All fixed a priori; no optimization.
WARMUP=50.

Usage:

```python
from strategies.bollinger_pctb import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the a-priori calibration rationale.

Sources:

- StockCharts Bollinger Bands / %B —
  https://school.stockcharts.com/doku.php?id=technical_indicators:bollinger_bands
- John Bollinger, *Bollinger on Bollinger Bands* (the %B
  indicator's original presentation).
