# Cup and Handle Breakout

William O'Neil's cup and handle, adapted to 1h crypto. A bullish
continuation pattern: a rounded consolidation (the cup) under a prior
high, a shallow pullback (the handle), then a volume-backed breakout.

- **Prior uptrend:** close > SMA(50) on each of the last 30 bars.
- **Cup:** left rim = highest high in the last 300 bars; bottom = lowest
  low after the left rim; cup duration 60–300 bars; cup depth 8–25% of
  the rim price AND 1–4x ATR(14); right rim = highest high after the
  bottom within 5% of the left rim.
- **Handle:** pullback after the right rim lasting ≤ 1/3 of the cup
  duration; handle low stays in the upper half of the cup; handle depth
  ≤ 1/3 of the cup depth.
- **Entry:** close above the handle high with volume > 1.4x the 20-bar
  average. The pattern must be complete by bar j−1; bar j is the
  breakout bar (no lookahead).
- **Long-only** (the pattern is bullish by construction; same convention
  as darvas_box). **Exits:** 1.5xATR stop (under the handle-low proxy),
  4.0xATR target (cup-depth projection proxy), 120-bar max hold.
- **Risk:** 1% equity risk/trade, 3x leverage cap, 0.045% fee + 0.01%
  slippage per side.

See BACKTEST.md for the 2026-03-14 → 2026-10-20 Hyperliquid 1h
(BTC/ETH/HYPE) results — zero trades: the specified dual depth filter
turns out to be mutually exclusive on 1h crypto — and CALIBRATION.md.
