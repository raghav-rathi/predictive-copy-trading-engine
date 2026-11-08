# Bollinger + RSI Mean Reversion

Bollinger Bands (20, 2) plus a short-period RSI(2): buy the washout only once price recovers back inside the band. Bands are SMA20 ± 2 × the 20-bar standard deviation of close; RSI(2) is Wilder RSI with period 2.

## Rules

- Long: bar i−1 closed below the lower band with RSI(2) < 10, and bar i closes back inside the band (close[i] > lower[i]) → enter on bar i.
- Short: mirror — bar i−1 closed above the upper band with RSI(2) > 90, and bar i closes back inside (close[i] < upper[i]) → enter on bar i.
- Exit a long on a close at/above the middle band (SMA20) or RSI(2) > 90. Exit a short on a close at/below the middle band or RSI(2) < 10.
- Bands and RSI are causal, so signals on bar i use only data through bar i's close. ATR stop / trail from the risk layer also applies.

## Source

- TradingCompendium — Mean Reversion Strategy: RSI + Bollinger Bands Rules: https://tradingcompendium.com/en/trading-strategies/mean-reversion-strategy-rsi-bollinger

Paper only, no live execution.
