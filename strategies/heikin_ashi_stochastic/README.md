# Heikin Ashi + Stochastic

Heikin Ashi trend filter plus a Stochastic %K/%D cross out of
oversold/overbought — buy the bounce only when the smoothed
trend agrees, sell the rollover only when it agrees.

## Rule

```
LONG when, on the same bar:
  HA bullish: ha_close > ha_open
  AND ha_close > ha_ema50 (EMA(50) of ha_close)
  AND %K crosses above %D (k[i] > d[i], k[i-1] <= d[i-1])
  AND %K < 30
SHORT is the mirror:
  HA bearish, ha_close < ha_ema50, %K crosses below %D,
  %K > 70
```

- **Exit long:** %K crosses below %D. **Exit short:** %K
  crosses above %D. No oversold/overbought condition on the
  exit — the cross alone is the momentum rollover.
- **Entries are transition-only** (state machine): a signal
  fires only when flat, or on a flip bar where an exit and
  the opposite entry land on the same bar. Repeated cross
  bars while a position is held do not re-enter.
- **Max hold:** 60 bars (~2.5 days on 1h).

## Indicators

- **Heikin Ashi:** ha_close = (o+h+l+c)/4,
  ha_open = (prev ha_open + prev ha_close)/2, seeded
  ha_open[0] = o[0]; ha_high/low are the max/min envelope.
  The recursion is causal (reads only the previous bar's HA
  values and the current bar's OHLC).
- **Stochastic (Fast %K, 3-period %D):** %K = 100 × (c −
  lowest low 14) / (highest high 14 − lowest low 14),
  %D = SMA(3) of %K, on regular closes. A zero 14-bar range
  (flat bars) gives %K = 50.0 (neutral), not 0/0. See
  CALIBRATION.md for the fast-vs-slow note: the spec's
  formulas define the fast form, so %K is the raw ratio, not
  the double-smoothed slow/full %K.

## Honest flag: the long gate is nearly shut

%K < 30 means price sits in the bottom 30% of its 14-bar
range, which usually means *below* its 50-bar average — so
requiring ha_close > ha_ema50 at the same time makes the
long condition rare by construction. On six seeded random
walks the long condition fired zero times (the short side
fired 1–4 times per 800 bars). On the real batch-45 window
longs did fire — 20 of 47 trades — but only on sharp
spike-and-pullback shapes where a recent high widens the
14-bar range enough for price to sit near its low while
still above the EMA(50). The system as specified is a
short-biased, low-frequency system (47 trades in ~8.3
months across three coins). That is a property of the spec,
not a bug — no gate was loosened to manufacture trades.
See BACKTEST.md and CALIBRATION.md.

## Risk

2×ATR(14) harness stop, 3×ATR(14) chandelier trail,
60-bar (~2.5-day) max hold, 1% risk per trade, 3× leverage
cap. WARMUP = 60 bars (EMA(50) + stochastic window, with
margin).

Source: Heikin Ashi (Munehisa Homma) + Stochastic Oscillator
(George Lane) — Heikin Ashi reference:
https://school.stockcharts.com/doku.php?id=chart_analysis:heikin_ashi
(verified live 2026-11-24); Stochastic %K/%D formulas per
StockCharts ChartSchool, "Stochastic Oscillator (Fast, Slow,
and Full)" — %K = 100 × (close − lowest low 14) / (highest
high 14 − lowest low 14), %D = 3-period SMA of %K.
