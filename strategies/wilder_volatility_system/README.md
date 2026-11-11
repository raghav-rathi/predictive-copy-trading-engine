# Wilder Volatility System

J. Welles Wilder's Volatility System (*New Concepts in Technical
Trading Systems*, 1978): buy when the close breaks above the previous
bar's high plus one ATR(7); sell when the close breaks below the
previous bar's low minus one ATR(7). The idea is that a close beyond
the previous bar's range expanded by a full ATR is a genuine volatility
expansion, not noise.

## Rules

- **Long entry:** close > previous bar's high + ATR(7).
- **Short entry:** close < previous bar's low - ATR(7).
- **Long exit / reverse:** the short trigger fires (close < previous
  bar's low - ATR(7)).
- **Short exit / reverse:** the long trigger fires.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies;
  the shipped system uses the harness stop/trail as the exit mechanism
  plus the reverse signal. Max hold 120 bars.
- Distinct from `wilder_volatility_stop`, which is only the
  trailing-stop component of Wilder's system — here the ATR breakout
  itself is the entry trigger.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- J. Welles Wilder, *New Concepts in Technical Trading Systems* (1978): https://www.investopedia.com/terms/v/volatility-system.asp

Paper only, no live execution.
