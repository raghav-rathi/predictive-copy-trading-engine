# Supertrend Parabolic

Supertrend(10, 3.0) + Parabolic SAR(0.02, 0.20) agreement: only
trade when both trend tools agree on direction — price above both
lines for longs, below both for shorts.

## Rules

- **Long entry:** the bar on which price becomes above BOTH the
  Supertrend line and the PSAR — the combined condition
  `(c > supertrend) & (c > psar)` is true now and was not true on
  the prior bar (agreement turns on).
- **Short entry:** mirror — the bar on which price becomes below
  BOTH lines.
- **Long exit:** close below the Supertrend line OR below the PSAR
  (either tool flips against the trade).
- **Short exit:** close above the Supertrend line OR above the PSAR.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

Supertrend is `strategies/base.py: supertrend`. PSAR is a
hand-rolled Wilder PSAR (base.py has no PSAR helper) implemented
as a causal forward loop: SAR starts at the first bar's low, AF
starts 0.02 and rises 0.02 per new extreme to a 0.20 cap, the SAR
never goes above the lows of the prior two bars in an uptrend /
below the highs of the prior two bars in a downtrend, and it flips
when price touches the SAR. All computation is causal, so signals
on bar i use only data through bar i's close.

## Source

- https://abouttrading.substack.com/p/applying-the-parabolic-sar-and-the
- https://www.gate.com/learn/articles/parabolic-sar-vs-supertrend-swing-trading

Paper only, no live execution.
