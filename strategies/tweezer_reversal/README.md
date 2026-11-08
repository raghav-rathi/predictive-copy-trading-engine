# Tweezer Reversal

Tweezer bottom/top reversal on 1h candles. After a trend (close below/above SMA(50) for the five bars before the pattern), two consecutive bars with near-equal lows/highs (within 0.1 × ATR(14)) and opposite candles, the second candle closing past the first candle's midpoint.

## Rules

- Tweezer bottom: downtrend (close below SMA(50) for the 5 bars before the pattern); bar 1 bearish, bar 2 bullish closing above bar 1's midpoint; |low2 − low1| ≤ 0.1 × ATR(14) → long entry on bar 2's close. Exit on a close below the tweezer low (min of the two lows).
- Tweezer top: mirror image — uptrend, bar 1 bullish, bar 2 bearish closing below bar 1's midpoint, |high2 − high1| ≤ 0.1 × ATR(14) → short entry. Exit on a close above the tweezer high (max of the two highs).
- The tweezer extremes are forward-filled from the pattern bar so the exit rule can reference them. ATR stop / trail from the risk layer also applies.

## Source

- Finviro — Japanese Candlestick Pattern Encyclopedia: https://finviro.com/en/academy/patterns

Paper only, no live execution.
