# Elder Ray: Bull/Bear Power around EMA(13)

Dr. Alexander Elder's momentum gauge from *Trading for a Living* —
the "Ray" component of his Triple Screen lineage.

## Mechanism

Every bar is decomposed around the trend baseline, EMA(13):

- **ema13** = EMA(close, 13)
- **bull_power** = high − ema13 — how far the bulls can lift the bar's
  high above "value"
- **bear_power** = low − ema13 — how far the bears can drag the bar's
  low below "value"

The classic Elder read: the EMA tells you *who owns the trend*; the
powers tell you *who owns the bar*. In an uptrend, you don't chase —
you wait for a dip (bear_power < 0) and enter when the bears start
losing their grip on it (bear_power rising). The mirror applies in
downtrends.

## Entries

- **Long:** EMA(13) slope up AND bear_power < 0 AND bear_power rising
  vs the prior bar — "buy the dip in an uptrend when the bears are
  weakening".
- **Short (mirror):** EMA(13) slope down AND bull_power > 0 AND
  bull_power falling.

## Exits

- **Long exit:** bear_power crosses above 0 (bears exhausted — the
  dip is over, momentum is mature) OR the EMA(13) slope turns down
  (uptrend structure broken).
- **Short exit:** bull_power crosses below 0 OR the EMA(13) slope
  turns up.

No fixed profit target: exits are signal-driven, backed by a
1.5xATR hard stop and a 2xATR chandelier trail, 120-bar (~5-day on
1h) max hold, 1% risk per trade, 3x leverage. Both sides enabled.

Parameters: EMA_N=13 (Elder's fixed constant), ATR(14). WARMUP=60.

Usage:

```python
from strategies.elder_ray import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))
res = BT.run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP, use_funding=False)
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the parameter note (fixed a priori, no tuning).

Sources:

- Elder Ray index mechanics —
  https://www.incrediblecharts.com/indicators/elder_ray_index.php
- Bull/Bear Power mechanics —
  https://In.Tradingview.com/support/solutions/43000717955-bull-bear-power/
