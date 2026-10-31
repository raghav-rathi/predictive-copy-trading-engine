# Hull MA Cross

Alan Hull's low-lag moving-average cross (2005): two Hull Moving
Averages, fast vs slow, crossed for entries and exits.

## Mechanism

WMA(c, n) is the linearly weighted moving average with weights
1..n, most recent bar heaviest:

- HMA(n) = WMA(2 × WMA(c, n/2) − WMA(c, n), √n)
- Fast: HMA(16) = WMA(2 × WMA(c, 8) − WMA(c, 16), 4)
- Slow: HMA(64) = WMA(2 × WMA(c, 32) − WMA(c, 64), 8)

Doubling the half-length WMA and subtracting the full-length WMA
removes most of the lag a plain average carries; the final short
WMA over √n bars re-smooths the result without reintroducing much
lag. The fast line therefore turns sooner than an EMA/SMA cross of
comparable smoothness — and also whipsaws sooner in chop, which is
the strategy's main weakness.

## Entry / exit

- **Long entry:** HMA(16) crosses above HMA(64).
- **Short entry:** HMA(16) crosses below HMA(64).
- **Exit:** the opposite cross. The risk layer adds a 2xATR stop, a
  2.5xATR trail, and a 120-bar max hold.

## Source

- Hull Moving Average, Alan Hull (2005), formula and default
  period 16:
  https://capital.com/en-int/learn/technical-analysis/hull-moving-average
  (verified; the HMA(16)/HMA(64) pairing is this strategy's own
  construction, not the source's.)

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1%
equity risk per trade, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, longs and shorts allowed. WARMUP = 80 bars
(64 for WMA(64) + 8 for the final WMA pass + ATR/margin).

## Honest limitation

HMA's lag removal is an extrapolation: around sharp reversals it
overshoots, so the fast line can cross and re-cross several times
in a single choppy stretch. The cross is a trend-following signal
with no volatility or trend-strength filter, so sideways markets
generate repeated small stop-outs (see BACKTEST.md).

Paper only, no live execution.
