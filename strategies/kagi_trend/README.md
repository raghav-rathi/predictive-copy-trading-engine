# Kagi Yang/Yin Trend

Trend-following on a close-based Kagi chart with a volatility-scaled
reversal amount (4 x ATR(14)). A column extends while price keeps moving
the same way; a reversal of 4xATR starts a new column.

- Line **thickens (yang)** when a rising column's high breaks the prior
  column's high ("shoulder") → **long**
- Line **thins (yin)** when a falling column's low breaks the prior
  column's low ("waist") → **short**
- **Exit:** the opposite yang/yin transition
- **Risk:** 2xATR hard stop, 100-bar max hold, 1% risk/trade, 3x leverage

See BACKTEST.md for the 2026-03-14 → 2026-10-19 Hyperliquid 1h
(BTC/ETH/HYPE) results and CALIBRATION.md for the 2x/4x/6x reversal
sensitivity check.
