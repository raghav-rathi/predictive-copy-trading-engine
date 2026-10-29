# Tasuki Gap Pattern

## Mechanism

The tasuki gap is Steve Nison's three-candle continuation
pattern: two same-color candles with a gap in the trend
direction, then a counter-color candle that pulls back into
the gap without closing it — the trend pauses, the gap holds,
the trend resumes.

- **Upside (long):** white candle, second white candle
  gapping up (open above the first close), then a black
  candle that opens inside the second candle's body and
  closes between the first candle's close and the second
  candle's close — a retracement that holds above the gap's
  origin. Uptrend filter: first candle's close above the
  close 5 bars earlier.
- **Downside (short):** mirror, with a downtrend filter.
- **First two bodies** each at least half their range.

**Continuous-market adaptation (read this before judging the
pattern):** the textbook rule has the third candle close
inside the literal gap (first close to second open). On a
24/7 crypto market that gap is a tick-size artifact — median
0.3–0.9% of one candle's range in this window — and the
literal rule fires ZERO times in ~16,300 bars (diagnosed in
CALIBRATION.md). The shipped rule widens only the
retracement bound, from the second candle's open to its
close: the counter candle must give back part of the second
candle's gain without violating the first candle's close.
The gap is still not closed; the pullback is just measured
against the second candle's close instead of its open.

## Entry / exit rules

- Long entry: upside tasuki bar while flat.
- Short entry: downside tasuki bar while flat.
- Long exit: a downside tasuki bar while long. Short exit
  mirrors.
- Risk layer: 2xATR stop, 2.5xATR trailing stop, 120-bar max
  hold, 1% risk per trade, 3x leverage cap.

## Source

Tasuki gap pattern (Steve Nison, Japanese Candlestick
Charting Techniques; Investopedia upside tasuki gap)
https://www.investopedia.com/terms/u/upside-tasuki-gap.asp

## Honest caveats

- The backtest (see BACKTEST.md) is mildly green (+$238 over
  42 trades, PF 1.14) — but that is $238 on $30k of starting
  capital across three coins, i.e. noise, and 39 of 42 exits
  are stops. The pattern is not a demonstrated edge.
- The adaptation above is a real deviation from the textbook
  rule, disclosed rather than hidden. Under the literal rule
  this strategy would have no trades at all on 1h crypto.
- Paper/backtest only. Nothing here touches live execution.
