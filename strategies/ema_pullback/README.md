# EMA Pullback

Classic trend-following pullback continuation: trade in the direction of the EMA(50) trend after price pulls back to touch the EMA(20) band and turns back in the trend direction.

## Rules

- Long only when close > EMA(50); short only when close < EMA(50).
- Pullback touch (long): within the last 5 bars, a bar low in [EMA(20) − 1.0×ATR(14), EMA(20) + 0.5×ATR(14)].
- Long entry: touch in the last 5 bars AND close > EMA(20) AND close > prior close. Short is the mirror image (bar high in [EMA(20) − 0.5×ATR, EMA(20) + 1.0×ATR]; close < EMA(20) and below prior close).
- Exit long: close < EMA(20); exit short: close > EMA(20).
- All price-vs-indicator comparisons use the prior bar's indicator values (shifted by 1).

## Source

- EMA pullback trend continuation (classic trend-following) — no verified URL.

Paper only, no live execution.
