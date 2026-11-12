# Bull Bear Power

Alexander Elder's Elder-Ray index (*Trading for a Living*, 1993):
Bull Power = high − EMA(13), Bear Power = low − EMA(13). The EMA is
the market's consensus value; the powers measure how far buyers and
sellers stretched price away from it on each bar. Elder's signal is
the turn: buy when Bear Power is negative but rising (sellers losing
strength) while Bull Power stays positive, sell on the mirror.

## Rules

- **Long entry:** Bear Power turns up (rising vs the prior bar) while
  still below zero AND Bull Power is above zero.
- **Short entry:** Bull Power turns down (falling vs the prior bar)
  while still above zero AND Bear Power is below zero.
- **Long exit:** the opposite turn (the short-entry condition).
- **Short exit:** the opposite turn (the long-entry condition).
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies;
  the shipped system uses the harness stop/trail as the exit mechanism
  plus the opposite turn. Max hold 120 bars.
- EMA(13) is Elder's own period; nothing was tuned to this window.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- Alexander Elder, *Trading for a Living* (1993): https://piprider.com/bulls-and-bears-power-indicators/

Paper only, no live execution.
