# Efficiency Ratio

Kaufman Efficiency Ratio trend filter gating an EMA cross — the cross
supplies timing and direction, ER supplies a quality gate that rejects
crosses produced by sideways noise.

## Mechanism

- **ER(10):** ER = |C - C[10]| / sum(|C_i - C_{i-1}| over the last 10
  bars). ER = 1 when price moves the same direction every bar of the
  window; ER = 0 when price ends where it started. A flat window
  (zero denominator) yields ER = 0. ER is the first step of Kaufman's
  KAMA construction (KAMA(10,2,30) uses a 10-period ER); this strategy
  uses the ER itself as a filter rather than building KAMA.
- **EMA cross:** EMA(9) vs EMA(21) on closes, via the shared `ema`
  primitive.

## Entry / exit

- **Long entry:** EMA(9) crosses above EMA(21) AND ER(10) > 0.3.
- **Short entry:** EMA(9) crosses below EMA(21) AND ER(10) > 0.3.
- **Long exit:** EMA(9) crosses below EMA(21) (no ER condition).
- **Short exit:** EMA(9) crosses above EMA(21) (no ER condition).
- The risk layer adds a 2xATR stop, a 2.5xATR trail, and a 120-bar max
  hold.

## Source

- Kaufman's Adaptive Moving Average / Efficiency Ratio (Perry Kaufman;
  ER definition, 10-period default, 0–1 range):
  https://chartschool.stockcharts.com/~gitbook/pdf?page=VEzdy31Qvi7cxEUjmhji&only=yes&limit=100
  (StockCharts ChartSchool KAMA page, verified; the ER > 0.3 gate and
  the EMA(9)/EMA(21) pairing are this strategy's own construction, not
  the source's.)

## Risk summary

2xATR stop, 2.5xATR trail, no fixed target, 120-bar max hold, 1% equity
risk per trade, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
longs and shorts allowed. WARMUP = 30 bars (EMA(21) needs 21 bars,
ER(10) needs 11).

## Honest limitation

ER > 0.3 is a weak gate: a sharp one-bar spike inside an otherwise
sideways window can lift ER above 0.3 without any real trend, and a
genuine trend that pauses for a few bars can drop ER below 0.3 and
block a valid cross. The stop still manages 86% of exits (see
BACKTEST.md), so the gate trims trade count without fixing the
underlying cross whipsaw.

Paper only, no live execution.
