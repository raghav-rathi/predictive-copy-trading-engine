# VIDYA Trend

Tushar Chande's Variable Index Dynamic Average (VIDYA), traded as a
price-cross system: long when the close crosses above VIDYA, short
when it crosses below. VIDYA is an EMA whose smoothing factor scales
with the strength of the recent trend, measured by the Chande
Momentum Oscillator — so it tracks fast when the trend is strong and
flattens when the market chops.

## Mechanism

- **CMO(9):** CMO = 100 * (UpSum - DnSum) / (UpSum + DnSum), where
  UpSum is the sum of positive close-to-close changes and DnSum the
  sum of absolute negative close-to-close changes over the 9 most
  recent changes (the change ending at the current bar and the 8
  before it). If UpSum + DnSum == 0 (flat market), CMO = 0.
- **Dynamic smoothing:** F = 2 / (20 + 1) = 2/21 (the standard EMA
  factor for period 20). alpha = F * |CMO| / 100. A perfectly
  trending window (CMO = ±100) gives alpha = 2/21, the full EMA(20)
  speed; a flat window (CMO = 0) gives alpha = 0 and VIDYA freezes.
- **Recursion:** VIDYA = alpha * close + (1 - alpha) * prev VIDYA,
  initialised to the close at the first valid bar (bar 9).

## Entry / exit

- **Long entry:** close crosses above VIDYA.
- **Short entry:** close crosses below VIDYA.
- **Exit:** the opposite cross (a cross bar both exits the open side
  and enters the other side). The risk layer adds a 2xATR stop, a
  2.5xATR trail, and a 120-bar max hold.

## Source

- Tushar Chande VIDYA, MetaTrader 5 indicator reference (verified,
  gives the EMA form, the CMO definition, and the VIDYA recursion):
  https://www.metatrader5.com/en/terminal/help/indicators/trend_indicators/vida
- CMO period 9 and EMA period 20 are this strategy's choices (the
  reference leaves both as parameters); the cross-trading rule is
  this strategy's construction.

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1% equity
risk per trade, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
longs and shorts allowed. WARMUP = 30 bars (CMO(9) lookback plus
margin for the recursion to settle).

## Honest limitation

VIDYA's adaptivity is one-sided: it slows in chop but never speeds
past EMA(20), so in a fast trend it still lags price, and in chop it
freezes while price oscillates around it — both regimes generate
crosses. The backtest shows the result: a ~20% win rate and a 0.72
profit factor (see BACKTEST.md). The freeze-in-chop property helps
less on 1h crypto bars than the theory suggests.
Paper only, no live execution.
