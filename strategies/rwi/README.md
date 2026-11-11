# Random Walk Index (RWI)

Chande & Kroll's Random Walk Index (*The New Technical Trader*, 1994):
compare the price range over the last 14 bars to the range a random
walk would typically cover in a single bar (measured by ATR).

- **RWI-high** = (high − low 14 bars ago) / ATR(14)
- **RWI-low** = (high 14 bars ago − low) / ATR(14)

A reading above 1.0 means price has moved further than a random walk
would typically travel in one bar — a genuine trend move, not noise.

## Rules

- **Long entry:** RWI-high crosses above 1.0.
- **Short entry:** RWI-low crosses above 1.0.
- **Long exit:** RWI-low crosses above 1.0 (the opposite RWI takes over).
- **Short exit:** RWI-high crosses above 1.0.
- ATR stop / trail from the risk layer also applies; max hold 120 bars.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- Chande & Kroll, *The New Technical Trader* (1994)
- Investopedia, "Random Walk Index": https://www.investopedia.com/terms/r/random-walk-index.asp

Paper only, no live execution.
