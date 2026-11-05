# Heikin Ashi Trend

Heikin Ashi trend (Dan Valcu, 2004): HA close = (o + h + l + c) / 4, HA open = (prev HA open + prev HA close) / 2, HA high = max(h, HA open, HA close), HA low = min(l, HA open, HA close). Long after 2 consecutive green HA candles following a red run while the real close is above EMA(50) of real closes; short mirror. Exit on the first opposite-colour HA candle. Stops are on real prices via the risk layer, never on HA values.

## Rules

- Long: 2 consecutive green HA candles, a red HA candle within the 10 bars before the run (the red run just ended), and real close above EMA(50).
- Short: 2 consecutive red HA candles, the candle before the run was green, and real close below EMA(50).
- Exit: first opposite-colour HA candle (plus ATR stop / trail on real prices).

## Source

- Heikin Ashi trading strategy (Dan Valcu): https://bjftradinggroup.com/heikin-ashi-trading-strategy/

Paper only, no live execution.
