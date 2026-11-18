# Change of Character (ChoCh)

The first break of market structure against the trend: in an
uptrend the protected higher low breaks on a displacement candle
(a ChoCh, not a full trend reversal), and the break is traded.

## Rules

- **Short entry:** the trend is an uptrend (last two swing highs
  rising AND last two swing lows rising) AND the close breaks
  below the protected higher low AND the breaking candle's body
  is displacement-sized (|close − open| > 1.5x ATR(14)).
- **Long entry:** the mirror in a downtrend against the protected
  lower high.
- **Long exit:** a bearish ChoCh prints OR the close exceeds the
  last swing high (the break failed / head exceeded).
- **Short exit:** a bullish ChoCh prints OR the close falls below
  the last swing low.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

Trend and protected levels are causal 5-bar pivots (centre+2
confirmation, recorded at the confirmation bar). The protected
swing in an uptrend is the swing low that produced the most recent
swing high (the latest swing low with centre before that high's
centre); in a downtrend the protected swing is the mirror. Trend
and protected levels are always read as of the previous bar: a
ChoCh must break structure established before the breaking bar,
never structure confirmed by that bar itself. Mixed structure
(one pair rising, one falling) retains the previous trend rather
than flipping to 0. All computation is causal, so signals on bar
i use only data through bar i's close.

## Sources

- GoForexHub, "BOS and ChoCh" —
  https://www.goforexhub.com/en/guides/trading-course-ict-smc-algo/bos-and-choch
- ICTradingConcepts, "ChoCh Trading" —
  https://ictradingconcepts.com/smc/choch-trading/

Paper only, no live execution.
