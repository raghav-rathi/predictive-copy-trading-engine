# Shooting Star Pattern

Steve Nison's shooting star (bearish) and its bullish mirror, the inverted hammer (*Japanese Candlestick Charting Techniques*, 1991): a small-bodied candle with a long shadow in the direction of the prevailing trend, signalling exhaustion.

## Rules

- Short: shooting star in an uptrend — close above prior-bar EMA(20) and 5-bar return above +1%. The star itself: body <= 30% of the bar's range, body bottom within the lower 35% of the range, upper shadow >= 2x body, lower shadow <= 10% of range.
- Long: inverted hammer in a downtrend — close below prior-bar EMA(20) and 5-bar return below -1%. The hammer itself: body <= 30% of range, body top within the upper 35% of the range, lower shadow >= 2x body, upper shadow <= 10% of range.
- Exit long: a shooting star appears. Exit short: an inverted hammer appears.
- Zero-range bars can never form a pattern. The pattern is read from the signal bar's own OHLC at its close; the harness executes at the next bar's open.

## Source

- Steve Nison shooting star (Japanese Candlestick Charting Techniques, 1991): https://www.quantum-algo.com/blog/guides/shooting-star-pattern-complete-guide/

Paper only, no live execution.
