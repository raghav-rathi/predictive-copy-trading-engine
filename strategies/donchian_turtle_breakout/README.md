# Donchian Turtle Breakout (System 1)

The original Turtle Traders system (Richard Dennis & William
Eckhardt, 1983, as documented by Curtis Faith in *Way of the
Turtle*): buy a breakout to a new 20-bar high, sell a breakout
to a new 20-bar low, and exit on a 10-bar Donchian channel
break in the other direction. The Turtles traded trend
breakouts with volatility-sized risk — 2×ATR stops — and let
winners run until the trend reversed.

## Rule (System 1)

```
LONG  on close > max(high of prior 20 bars)
SHORT on close < min(low of prior 20 bars)
Exit LONG  on close < min(low of prior 10 bars)
Exit SHORT on close > max(high of prior 10 bars)
```

- **Channel excludes the current bar.** The 20-bar high is the
  max high of bars i−20..i−1, so a bar can never break out on
  its own high — the level was known before the bar opened.
- **Stop:** 2×ATR(20) via the harness.
- **No pyramiding:** one position at a time; repeated breakout
  bars while holding do not add.
- **Max hold:** 336 bars (~14 days on 1h).

## System 1 only — documented deviations

- **No System 2.** The 55-day entry / 20-day exit system is
  not implemented; this is System 1 (20-day entry, 10-day
  exit) only.
- **Skip rule NOT implemented.** The Turtles skipped a breakout
  if the previous breakout in that market had been a winner
  (to avoid chasing a trend already in motion). This
  implementation takes every breakout — a deliberate,
  documented deviation from the spec. It means the system
  trades more often than the original, including breakouts
  into already-extended moves.
- **1h scaling.** The original is a daily system (20-day /
  10-day channels). Here 20 bars = 20 hours and 10 bars = 10
  hours, so the "trend" being traded is an intraday one — far
  choppier than the daily original. Expect many more trades
  and many more whipsaws; see BACKTEST.md.

## Honest flag: 1h breakouts whipsaw

On 1h crypto, a 20-bar high is broken constantly by noise.
The backtest fires 510 trades across three coins in eight
months (~2 per coin per week) with a 29.6% win rate — the
classic Turtle profile of many small losses and a few big
wins, except on this window the big wins did not arrive often
enough on BTC. See BACKTEST.md.

## Risk

2×ATR(20) harness stop, no trail, no target, 336-bar (~14-day)
max hold, 1% risk per trade, 3× leverage cap. WARMUP = 60
bars (20-bar channel + 20-bar ATR, with margin).

Source: Curtis Faith, *Way of the Turtle* (2007) — Turtle
trading, System 1 (https://en.wikipedia.org/wiki/Turtle_trading).
