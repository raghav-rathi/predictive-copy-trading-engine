# Wyckoff Upthrust (Short Only)

A failed breakout above a trading range — the classic Wyckoff
distribution signature. Breakout buyers get trapped when price cannot
hold above the range; the short rides the snap back inside it.

## Mechanism

- **Trading range, prior bars only:** range_high = max high over the
  20 bars before the current bar; range_low = min low over the same
  20 bars (rolling extremes shifted by 1). The current bar never
  enters its own range.
- **Upthrust bar:** high > range_high AND close < range_high AND
  close > range_low — price breaks above the range, then closes back
  inside it.

## Entry / exit

- **Short entry:** an upthrust bar (executes at the next bar's open).
- **Short exit:** close crosses above range_high — the upthrust
  thesis failed, price reclaimed above the range. The risk layer adds
  a 2xATR stop, a 2.5xATR trail, and a 120-bar max hold.
- **Longs:** never. Long entry and long exit are always False.

## Source

- Wyckoff Method Trading (upthrust = a move above the high of the
  range that fails; price breaks above, then reverses and closes back
  below the range high — the signature of distribution):
  https://www.tradingsim.com/blog/wyckoff-method-trading
  (verified via search; the 20-bar prior-range construction and the
  reclaim exit are this strategy's own formalization, not the
  source's.)

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01% slippage
per side, shorts only. WARMUP = 25 bars.

## Honest limitation

The formalization is deliberately bare: it does not check volume
(classic Wyckoff weighs the upthrust's volume), does not require the
range to be a genuine distribution range (any 20-bar window counts),
and does not demand a sign of weakness after the upthrust. In a
strong uptrend, "failed" breakouts keep resolving upward, and the
2xATR stop takes the loss — see BACKTEST.md. Paper only, no live
execution.
