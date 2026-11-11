# TEMA Cross

Patrick Mulloy's Triple Exponential Moving Average (TEMA), traded as a
pure 9/21 cross: TEMA(9) above TEMA(21) is long, below is short. TEMA
removes most of the lag of a single EMA by combining three nested
smoothings: TEMA(n) = 3*EMA1 - 3*EMA2 + EMA3.

## Rules

- **Long entry:** TEMA(9) crosses above TEMA(21).
- **Short entry:** TEMA(9) crosses below TEMA(21).
- **Long exit:** TEMA(9) crosses back below TEMA(21) (opposite cross).
- **Short exit:** TEMA(9) crosses back above TEMA(21).
- **No regime filter.** This is what distinguishes it from the existing
  `tema_trend` strategy (TEMA 20/50 cross + SMA200 filter): here the
  cross itself is the whole system, so it trades every cross including
  choppy ones.
- ATR stop / trail from the risk layer also applies; max hold 120 bars.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- Patrick Mulloy, TEMA: https://abovethegreenline.com/what-is-the-triple-exponential-moving-average-tema/
- https://www.definedgesecurities.com/library/tema/

Paper only, no live execution.
