# SMA-RSI Pullback

RSI pullback in trend. Uptrend is SMA50 > SMA200; a pullback bar is one whose low touches or dips to the 50 SMA while RSI(14) is in 40–55. Entry on the first bar within 5 bars after a pullback bar whose close is back above SMA50. Mirror for shorts.

## Rules

- Long: SMA50 > SMA200. Pullback bar: low ≤ SMA50 with RSI(14) in 40–55. Enter long on the first close back above SMA50 (a close crossing back up through SMA50) within 5 bars of a pullback bar. Exit on RSI(14) > 70 or a close below SMA200.
- Short: SMA50 < SMA200. Pullback bar: high ≥ SMA50 with RSI(14) in 45–60. Enter short on the first close back below SMA50 within 5 bars of a pullback bar. Exit on RSI(14) < 30 or a close above SMA200.
- Pullback bars and the cross-back are evaluated on closes through the signal bar only, so signals use no future data. ATR stop / trail from the risk layer also applies.

## Source

- Vocal Media — The RSI Pullback Strategy: https://vocal.media/trader/the-rsi-pullback-strategy

Paper only, no live execution.
