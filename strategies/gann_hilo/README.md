# Gann HiLo Activator

The Gann Hi-Lo Activator (Robert Krausz, 1998 — despite the name, not Gann's) is a two-line state machine: while bullish it plots the SMA(3) of lows as support, while bearish the SMA(3) of highs as resistance. The state flips only when price closes beyond the previous bar's opposite SMA, so the line is a breakout filter, not a moving average to cross casually.

## Mechanism

- SMA(3) of highs and SMA(3) of lows, computed from prior bars.
- State +1 when close > previous SMA(high); -1 when close < previous SMA(low); otherwise unchanged.
- Plotted line: SMA(low) while bullish, SMA(high) while bearish.

## Entry / exit

- **Long entry:** state flips to +1.
- **Short entry:** state flips to -1.
- **Exit:** the opposite flip. The risk layer adds a 2xATR stop, a 2.5xATR trail, and a 120-bar max hold.

## Source

- Gann Hi-Lo Activator (Robert Krausz, Stocks & Commodities 1998):
  https://financial-hacker.com/petra-on-programming-the-gann-hi-lo-activator/

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 20 bars
(3 bars for the SMAs + ATR/margin.).

## Honest limitation

With a 3-bar SMA the flip threshold sits very close to price, so volatile 1h bars flip the state often and the system pays the spread on both sides of chop. The activator is a trend-permission line in its original swing system (paired with DMI and SMI); traded alone it has no confirmation filter (see BACKTEST.md).

Paper only, no live execution.
