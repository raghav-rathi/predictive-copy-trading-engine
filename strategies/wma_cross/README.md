# WMA Crossover

Linearly weighted moving average crossover. WMA(n) weights the last n closes linearly with the newest close weighted n and the oldest 1: WMA[i] = Σ (n−k)·close[i−k] / (n·(n+1)/2). It reacts faster than an SMA of the same length because recent bars dominate. WMA(9) vs WMA(21): the fast line reacts sooner, the slow line lags, and their cross marks a trend change.

## Rules

- Long: WMA(9) crosses above WMA(21). Exit on WMA(9) crossing below WMA(21).
- Short: WMA(9) crosses below WMA(21). Exit on WMA(9) crossing above WMA(21).
- All computation is causal, so signals on bar i use only data through bar i's close. ATR stop / trail from the risk layer also applies.

## Source

- Investopedia — Weighted Moving Average (WMA): https://www.investopedia.com/terms/w/weightedmovingaverage.asp

Paper only, no live execution.
