# Central Pivot Range

Frank Ochoa's Central Pivot Range: three levels from the prior
UTC day — Pivot, Top Central, Bottom Central — forming a value
area. Price holding above the range is bullish, below it bearish,
and a breakout through the range's edge is the entry.

## Mechanism

- From the prior UTC day's H, L, C: Pivot = (H+L+C)/3,
  BC = (H+L)/2, TC = 2×Pivot − BC.
- Levels are fixed for the whole current day (computed from a
  completed day only, so no lookahead).
- A narrow TC−BC zone forecasts an explosive day; a wide zone
  forecasts a range day.

## Entry / exit

- **Long entry:** close crosses above the prior day's TC.
- **Short entry:** close crosses below the prior day's BC.
- **Exit:** close crosses back through the prior day's Pivot.
  The risk layer adds a 2xATR stop, a 2.5xATR trail, and a 120-bar
  max hold.

## Source

- Central Pivot Range (Frank Ochoa):
  https://www.stockmaniacs.net/central-pivot-range/

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 48 bars
(24 bars for one full UTC day + margin.).

## Honest limitation

Daily levels on 1h bars are step functions: price can cross TC,
fall back, and re-cross several times in one day, and every cross
is a fresh entry. Crypto trades 24/7, so the 'UTC day' boundary is
arbitrary — a level built from an arbitrary window carries no
structural meaning (see BACKTEST.md).

Paper only, no live execution.
