# Quasimodo Reversal

The Quasimodo (over-and-under) pattern: a higher high that breaks
structure, then a retracement that fails to reach the head and
forms a lower shoulder — the failed retest of the left shoulder
is the entry.

## Rules

- **Short entry (bearish QM):** H1 swing high, then a lower swing
  low L1, then a higher swing high H2 (the head), then a close
  below L1 (the break), then a retracement back above L1 that
  stays below H2 and forms a swing low RL (the shoulder) — short
  on a close below RL.
- **Long entry (bullish QM):** the mirror — L1 swing low, H1 swing
  high, lower swing low L2 (the head), close above H1, retracement
  back below H1 staying above L2, swing high RH — long on a close
  above RH.
- **Long exit:** an opposite bearish-QM signal OR a close below
  the bullish head low (invalidation).
- **Short exit:** an opposite bullish-QM signal OR a close above
  the bearish head high (invalidation).
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

Swings are causal 5-bar pivots: a swing high at centre j iff
h[j] is the max of h[j-2..j+2], recorded at the confirmation bar
(centre+2), never at the centre bar. The shoulder swing low must
sit above the lowest low printed since the break, and the
retracement must actually get back across the broken level (above
L1 for bearish, below H1 for bullish). All computation is causal,
so signals on bar i use only data through bar i's close.

## Sources

- The Right Trader, "Quasimodo Pattern":
  https://therighttrader.com/learn/chart-patterns/quasimodo-pattern
- Pivex, "Quasimodo Pattern":
  https://pivex.com/blog/quasimodo-pattern

Paper only, no live execution.
