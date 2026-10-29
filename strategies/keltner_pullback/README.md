# Keltner Pullback

## Mechanism

Trend + pullback, not breakout. The Keltner channel's midline
(EMA20) is the value zone inside a trend: in an uptrend,
price dipping to or through the midline and then closing back
above it is a discount re-entry, not a breakdown. That is the
whole difference from the existing Keltner strategies —
`keltner_rsi` and `keltner_adx` trade closes OUTSIDE the band
with a filter, and `keltner_squeeze` trades band-width
contraction. None of them trades the midline pullback:

- **Keltner channel:** midline EMA20, bands at midline ±
  1.5 × ATR(10) (the `keltner` primitive in
  `strategies/base.py`).
- **Trend filter:** close above a rising EMA50 (long) or
  below a falling EMA50 (short). The EMA50 trend must survive
  the pullback itself — a dip that breaks the EMA50 trend is
  not a pullback, it is a reversal, and it does not trade.
- **Long entry:** close crosses back above the Keltner
  midline while in an EMA50 uptrend. The cross itself
  guarantees a pullback happened: the prior close was on the
  far side of the midline.
- **Short entry:** mirror — cross back below the midline in
  an EMA50 downtrend.
- **Exit:** the opposite midline cross (the thesis has failed
  a second time), plus the risk layer: 2xATR stop, 3xATR
  trail, 120-bar (5-day) max hold.

## Entry / exit rules

- Long entry: cross back above kc_mid with close above a
  rising EMA50, while flat.
- Short entry: cross back below kc_mid with close below a
  falling EMA50, while flat.
- Long exit: close crosses back below kc_mid. Short exit
  mirrors.
- Risk layer: 2xATR stop, 3xATR trailing stop, 120-bar max
  hold, 1% risk per trade, 3x leverage cap.

## Source

Keltner channels (Chester Keltner; StockCharts ChartSchool)
https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/keltner-channels

## Honest caveats

- The backtest (see BACKTEST.md) is the worst of this batch
  by a wide margin: -$11,461 over 1,253 trades, with BTC at
  -55.6% max drawdown and a 20.6% win rate. The midline cross
  fires constantly in chop — 1,253 trades in 7 months is
  ~6 per day across three coins — and most of them are
  whipsaws: 865 of 1,253 exits are the opposite-cross signal
  exit, i.e. the trade immediately reversing on the next
  midline touch.
- The EMA50 trend filter does not save it: on 1h crypto,
  price spends long stretches oscillating around a flat-ish
  EMA50, and "above a rising EMA50" is satisfied through
  most of those oscillations.
- Paper/backtest only. Nothing here touches live execution.
