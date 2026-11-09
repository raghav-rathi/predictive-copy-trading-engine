# SMMA Crossover

Wilder's Smoothed Moving Average crossover. SMMA(n) is seeded with the simple average of the first n closes, then smoothed with alpha = 1/n: SMMA[i] = (SMMA[i-1] × (n−1) + close[i]) / n. It is the same smoothing Wilder used inside RSI and ADX. SMMA(9) vs SMMA(21): the fast line reacts sooner, the slow line lags, and their cross marks a trend change.

## Rules

- Long: SMMA(9) crosses above SMMA(21). Exit on SMMA(9) crossing below SMMA(21).
- Short: SMMA(9) crosses below SMMA(21). Exit on SMMA(9) crossing above SMMA(21).
- All computation is causal, so signals on bar i use only data through bar i's close. ATR stop / trail from the risk layer also applies.

## Source

- J. Welles Wilder, *New Concepts in Technical Trading Systems* (1978) — SMMA definition
- Smoothed moving average: https://en.wikipedia.org/wiki/Moving_average#Smoothed_moving_average

Paper only, no live execution.
