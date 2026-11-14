# Renko Brick Reversal

Classic Renko charting (Japanese "renga", brick) traded as a
2-brick reversal system.

- **Brick size** = mean ATR(14) over the first 200 bars, fixed per
  coin: BTC $507.48, ETH $20.87, HYPE $0.60 on the batch window
- **Bricks** print from 1h closes (a close-based approximation of
  tick Renko — intrabar excursions that never close beyond a brick
  edge are invisible): a new brick forms when the close clears the
  last brick's top by one brick size (up) or its bottom by one
  brick size (down). A reversal needs two brick sizes against the
  last brick — the classic Renko reversal rule.
- **Trend** = direction of the last 2 bricks
- **Long:** a bullish 2-brick reversal completes after a downtrend
  of ≥ 3 down bricks
- **Short:** a bearish 2-brick reversal completes after an uptrend
  of ≥ 3 up bricks
- **Exit:** the opposite 2-brick reversal
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 200-bar max
  hold, 1% risk/trade, 3x leverage

Parameters: brick = 1.0x ATR(14) (first-200-bar mean), ATR(14) for
stop/trail. WARMUP=220.

Usage:

```python
from strategies.data import fetch_candles
from strategies.renko_brick_reversal import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the brick-size sensitivity check.

Source: Renko chart —
https://www.cmcmarkets.com/en-gb/technical-analysis/renko-charts

## Honest caveats

- This is a close-based approximation of Renko, not tick Renko:
  bricks can only complete at 1h closes, so a fast intraday reversal
  that closes back inside the brick is never seen.
- The entry fires after price has already travelled 2+ brick sizes
  in the new direction (plus the ≥ 3-brick run it reversed), so the
  trade is chasing a move that is already extended; the 2xATR stop
  sits close behind and gets hit first in most trades (see
  BACKTEST.md — 205 of 245 exits were stops).
- The brick size is fixed from the first 200 bars of the window; a
  volatility regime change later in the window makes the brick too
  big (few signals) or too small (whipsaw bricks).
