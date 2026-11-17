# CCI + MACD Combo

A mean-reversion trigger with a trend filter: CCI(14) fires when
price stretches to an extreme and snaps back through the ±100
level, but only when MACD agrees with the direction — the MACD
line above its signal line for longs, below it for shorts.

## Rules

- **CCI(14):** typical price TP = (h + l + c) / 3;
  CCI = (TP - SMA(TP, 14)) / (0.015 * mean deviation), where the
  mean deviation is the 14-bar rolling mean of |TP - SMA(TP, 14)|.
- **MACD(12, 26, 9)** on the raw close.
- **Long entry:** CCI crosses up through -100 while the MACD line
  is above its signal line.
- **Short entry:** CCI crosses down through +100 while the MACD
  line is below its signal line.
- **Long exit:** CCI crosses back down through 0.
- **Short exit:** CCI crosses back up through 0.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

CCI is first defined at bar 26, not bar 13: the SMA needs 14 bars
and the deviation mean needs 14 defined deviations. Warmup 60
covers this comfortably. All computation is causal, so signals on
bar i use only data through bar i's close.

## Source

- The Forex Geek, "CCI + MACD strategy":
  https://theforexgeek.com/cci-macd-strategy/
- UMA Technology, "Forex trading strategy 50 — MACD + CCI":
  https://umatechnology.org/forex-trading-strategy-50-macd-cci/

Paper only, no live execution.
