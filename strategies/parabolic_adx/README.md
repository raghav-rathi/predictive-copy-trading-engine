# Parabolic ADX

Parabolic SAR(0.02, 0.20) flip gated by ADX(14) trend strength —
Wilder's own pairing: the SAR gives the turn, ADX confirms a
trend is actually strong enough to trade.

## Rules

- **Long entry:** PSAR flips from above price to below price on
  this bar (`psar < c` and `psar.shift(1) > c.shift(1)`) AND
  ADX > 25 AND +DI > -DI.
- **Short entry:** PSAR flips from below price to above price AND
  ADX > 25 AND -DI > +DI.
- **Long exit:** PSAR flips above price OR ADX < 20 (trend
  exhausted).
- **Short exit:** PSAR flips below price OR ADX < 20.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

PSAR is a hand-rolled Wilder PSAR (base.py has no PSAR helper)
implemented as a causal forward loop: SAR starts at the first
bar's low, AF starts 0.02 and rises 0.02 per new extreme to a
0.20 cap, the SAR never goes above the lows of the prior two bars
in an uptrend / below the highs of the prior two bars in a
downtrend, and it flips when price touches the SAR. ADX/+DI/-DI
are `strategies/base.py: adx`. All computation is causal, so
signals on bar i use only data through bar i's close.

## Source

- https://unofficed.com/courses/mastering-market-indicators/lessons/combining-parabolic-sar-with-adx/?ld-lesson-page=2
- https://www.babypips.com/learn/forex/parabolic-sar

Paper only, no live execution.
