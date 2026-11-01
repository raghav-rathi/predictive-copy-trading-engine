# NR7 Breakout

Toby Crabel's Narrow Range 7: the bar with the smallest high-low
range of the last seven marks a volatility contraction. Contraction
precedes expansion, so the breakout from the NR7 bar's range is the
entry — valid for 24 bars, after which the setup expires.

## Mechanism

- Range = high − low. An NR7 bar's range is smaller than each of
  the previous six bars' ranges.
- The setup levels are the NR7 bar's own high and low.
- A close above the high = upside breakout; below the low =
  downside breakout. The setup expires 24 bars after the NR7 bar.

## Entry / exit

- **Long entry:** close crosses above the live NR7 bar's high.
- **Short entry:** close crosses below the live NR7 bar's low.
- **Exit:** close crosses the opposite side of the NR7 range
  (failed breakout). The risk layer adds a 2xATR stop, a 2.5xATR
  trail, and a 120-bar max hold.

## Source

- NR7 (Toby Crabel):
  https://therobusttrader.com/title-nr7-trading-strategy-the-narrow-range-7-by-toby-crabel/

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 20 bars
(7 bars for the NR7 window + ATR(14) + margin.).

## Honest limitation

NR7 was designed for daily bars; on 1h bars a 'narrowest of 7'
bar prints constantly, so setups overlap and the 24-bar expiry
chops the signal. Most 1h NR7 breakouts are noise expansions that
reverse within a few bars (see BACKTEST.md).

Paper only, no live execution.
