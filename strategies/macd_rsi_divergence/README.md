# MACD + RSI Divergence (MACD-only)

Regular divergence: price makes a new extreme but momentum
does not confirm it — a lower low with a higher MACD histogram
(bullish), or a higher high with a lower histogram (bearish).
The divergence is traded on the confirmation bar, with the
histogram's direction as the trigger.

## Rule

```
Bullish divergence: confirmed pivot low LOWER than the previous
  confirmed pivot low, AND MACD histogram at the new pivot HIGHER
  than at the previous pivot low.
  LONG on the confirmation bar IF histogram is rising
  (hist[i] > hist[i-1]).
Bearish divergence: mirror (higher pivot high, lower histogram).
  SHORT on the confirmation bar IF histogram is falling.
```

- **Confirmed pivot:** a low is confirmed when it is the strict
  lowest low of the ±2-bar window around it; the signal is
  available on the confirmation bar (pivot bar + 2). Same for
  highs. Strict inequality avoids duplicate pivots on flat
  equal lows/highs.
- **Exit long:** MACD histogram crosses below zero, OR a new
  bearish divergence is confirmed. **Exit short:** the mirror.
- **Max hold:** 120 bars (~5 days on 1h).

## Honest flag: MACD-only, despite the name

The slug is `macd_rsi_divergence`, but this implementation is
**MACD-only for both sides, per the build spec. RSI divergence
was NOT implemented.** RSI(14) is computed and exposed as a
column for inspection, but no signal reads it. Do not cite this
strategy as an RSI-divergence system.

## Honest flag: entries lag the turn by design

Divergence needs two pivots, and each pivot needs 2 bars of
confirmation — so the entry fires at least 2 bars after the
pivot low, and the pivot low itself is only recognizable after
the price has already started recovering. By the time the long
fires, the turn is already several bars old and part of the
move is gone. That lag is structural, not a bug: the system
trades confirmed momentum failure, not the low itself. On a
fast V-reversal the entry can arrive after most of the bounce;
on a slow grind down it can catch the turn. See BACKTEST.md.

## 1h scaling notes

- MACD is the classic (12, 26, 9). On 1h bars the histogram
  crosses zero frequently, so the zero-cross exit is the
  dominant exit (see BACKTEST.md) and holding periods are
  short.
- The ±2-bar pivot window is 2 hours of confirmation — tight
  for 1h crypto, so pivots fire often and divergences are
  common (~1 per coin per 1.5 days in the backtest).

## Risk

2×ATR(14) harness stop, no trail, no target, 120-bar (~5-day)
max hold, 1% risk per trade, 3× leverage cap. WARMUP = 60
bars (26-bar slow EMA + pivot confirmation, with margin).

Source: Gerald Appel (MACD) + classic divergence literature
(Bulkowski, *Encyclopedia of Chart Patterns*)
(https://thepatternsite.com/Divergence.html).
