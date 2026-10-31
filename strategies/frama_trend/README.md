# FRAMA Trend

John Ehlers' Fractal Adaptive Moving Average (FRAMA), N = 16, traded
as a price-cross system: long when the close crosses above FRAMA,
short when it crosses below. The smoothing factor adapts to the
fractal dimension of recent price action — fast in clean trends, slow
in congestion — instead of using a fixed EMA span.

## Mechanism

- **Price:** price = (H + L) / 2.
- **Range components (per-bar ranges):**
  - N1 = (highest high - lowest low over the most recent 8 bars) / 8.
  - N2 = (highest high - lowest low over the preceding 8 bars) / 8.
  - N3 = (highest high - lowest low over all 16 bars) / 16.
- **Fractal dimension:** D = (log(N1 + N2) - log(N3)) / log(2),
  clamped to [1, 2]. A straight trend gives D near 1; congestion
  pushes D toward 2.
- **Adaptive alpha:** alpha = exp(-4.6 * (D - 1)), clamped to
  [0.01, 1]. In a clean trend alpha approaches 1 (FRAMA tracks price
  almost bar-for-bar); in congestion alpha approaches 0.01 (heavy
  smoothing).
- **Recursion:** FRAMA = alpha * price + (1 - alpha) * prev FRAMA,
  initialised to the price at the first valid bar (bar 15). A zero
  range (perfectly flat prices) makes D undefined; it is treated as
  D = 2 (maximum congestion).

## Entry / exit

- **Long entry:** close crosses above FRAMA.
- **Short entry:** close crosses below FRAMA.
- **Exit:** the opposite cross (a cross bar both exits the open side
  and enters the other side). The risk layer adds a 2xATR stop, a
  2.5xATR trail, and a 120-bar max hold.

## Source

- John Ehlers FRAMA writeup, "The Continuing Search For Robust
  Momentum Indicators" (R-bloggers / QuantStrat TradeR, verified):
  https://www.r-bloggers.com/2014/06/the-continuing-search-for-robust-momentum-indicators-the-fractal-adaptive-moving-average/
- N = 16 is this strategy's choice (the source uses N = 20 as its
  default and notes N must be even); the cross-trading rule is the
  simple strategy the source itself describes. The alpha formula
  exp(-4.6 * (D - 1)) with the [0.01, 1] clamp is this strategy's
  direct implementation of Ehlers' specification.

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1% equity
risk per trade, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
longs and shorts allowed. WARMUP = 40 bars (N = 16 lookback plus
margin for the recursion to settle).

## Honest limitation

At N = 16 the FRAMA hugs price closely in trends (alpha near 1), so
crosses fire very often — ~1,000 trades per coin over this window —
and the source itself warns the fast FRAMA "tracks price too well"
and whipsaws. The backtest confirms it: a 22% win rate and a 0.67
profit factor (see BACKTEST.md). A slower N would cross less but
that would be a different, tuned strategy, not this one.
Paper only, no live execution.
