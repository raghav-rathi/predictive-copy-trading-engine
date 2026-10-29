# Kicker Pattern

## Mechanism

The kicker (kicking) pattern is Steve Nison's two-candle
surprise reversal: the first candle runs with the trend and the
second gaps in the opposite direction and closes strongly that
way, an abrupt sentiment flip usually tied to news. The gap test
used here is Nison's kicking definition: the second candle's
open must lie beyond the first candle's open, in the new
direction.

- **Bullish:** bar 1 black (close < open), bar 2 white with
  open above bar 1's open (o2 > o1) and a body at least half
  its range.
- **Bearish:** mirror — bar 1 white, bar 2 black with o2 < o1,
  body at least half its range.
- **No trend filter:** the kicking reference notes the
  preceding trend is of little importance for this pattern —
  the gap itself is the signal.

Note why this pattern is rare on 1h crypto: with opens
tracking prior closes, o2 > o1 after a black bar 1 requires a
gap larger than bar 1's whole body. That is the textbook
definition, not a bug — it fired only 5 times in ~16,350 bars.

## Entry / exit rules

- Long entry: bullish kicker bar while flat.
- Short entry: bearish kicker bar while flat.
- Long exit: a bearish kicker bar while long. Short exit
  mirrors.
- Risk layer: 2xATR stop, 2.5xATR trailing stop, 72-bar max
  hold, 1% risk per trade, 3x leverage cap.

## Source

Kicker / kicking pattern (Steve Nison, Japanese Candlestick
Charting Techniques; CentralCharts candlestick reference)
https://www.centralcharts.com/en/gm/1-learn/7-technical-analysis/28-japanese-candlesticks/552-kicking

## Honest caveats

- The backtest (see BACKTEST.md) loses a little (-$76 over
  just 5 trades): one ETH winner (+$235) against four
  stop-outs. With 5 trades no statistical claim is possible —
  this is a "rare pattern, no evidence" result, not a verdict
  on Nison's pattern in general.
- On a 24/7 market, genuine kicking gaps are scarce; most
  "kickers" a loose screener finds are ordinary opens, not
  gaps beyond the prior open. Loosening the gap test to
  o2 > c1 would multiply signals but would no longer be the
  kicker pattern.
- Paper/backtest only. Nothing here touches live execution.
