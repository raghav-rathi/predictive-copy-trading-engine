# Intraday Momentum Index

Tushar Chande's Intraday Momentum Index: an RSI-style oscillator built on open-to-close movement inside each bar instead of close-to-close changes. Over 14 bars, IMI = 100 × (sum of intraday gains) / (sum of intraday gains + sum of intraday losses); a window with no intraday movement at all reads 50. A bar that closes well above its open adds to the gain sum, a bar that closes well below its open adds to the loss sum — so IMI measures whether the day's (hour's) closes are landing near the highs or the lows of their own bars.

## Rules

- Long: IMI crosses up through 30 (leaving oversold). Exit on IMI crossing above 70.
- Short: IMI crosses down through 70 (leaving overbought). Exit on IMI crossing below 30.
- All computation is causal, so signals on bar i use only data through bar i's close. ATR stop / trail from the risk layer also applies.

## Source

- Tushar Chande, *The New Technical Trader* (Intraday Momentum Index)
- Formula reference: https://doc.stocksharp.com/en/topics/api/indicators/list_of_indicators/intraday_momentum_index

Paper only, no live execution.
