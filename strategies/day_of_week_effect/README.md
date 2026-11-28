# Day-of-Week Effect (Bitcoin)

Bitcoin weekday seasonality, fixed from the literature
(Decourt, Chohan & Perugini 2017; Caporale & Plastun 2018;
FairHatch 2026 Binance daily data): Mondays relatively
strong, Thursdays the weakest weekday. The shipped config
is LONG Mondays, SHORT Thursdays (UTC).

- **Long Monday:** long_entry fires on the bar with
  weekday == Sunday and hour == 23 (harness executes at
  Monday 00:00 open); long_exit fires on weekday == Monday
  and hour == 23 (executed Tuesday 00:00).
- **Short Thursday:** short_entry fires on weekday ==
  Wednesday and hour == 23 (executed Thursday 00:00 open);
  short_exit fires on weekday == Thursday and hour == 23
  (executed Friday 00:00).
- **One bar per week:** each signal fires on exactly one
  bar per week by construction (a single weekday+hour
  combination), so there is no re-fire issue -- this is the
  documented exception to the house CROSS-based entry rule.
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 30-bar
  max hold (a leg is held ~24 bars by the clock; the hold
  is a backstop, not the exit), 1% risk/trade, 3x leverage

Parameters: none tuned -- the legs, days, and hours are
fixed from the literature before any backtest. ATR(14) for
risk, WARMUP 30 bars.

Deviations / implementation notes (all documented, none
tuned to PnL):

- The literature is on daily bars; the 23:00-bar signalling
  is purely the harness's next-open execution convention --
  the economic leg is the full Monday / Thursday UTC day.
- The Wednesday-long calibration variant (see
  CALIBRATION.md) enters Tuesday 23:00 and exits Wednesday
  23:00, so its exit and the Thursday short entry share the
  Wednesday 23:00 bar; the harness exits first and enters
  second at the same open, so the legs do not collide.

Sources: Monday effect in Bitcoin -- Decourt, Chohan &
Perugini 2017; Caporale & Plastun 2018 (MPRA paper 91429)
-- https://mpra.ub.uni-muenchen.de/id/eprint/91429/contents
-- and FairHatch 2026 Binance daily data (Thursday the
weakest weekday, 2017-2026).

Usage:

```python
from strategies.day_of_week_effect import indicators, signals, risk

df = indicators.add_indicators(df)
sig = signals.add_signals(df)  # shipped: Mon long + Thu short
```

See BACKTEST.md for the 2026-03-14 -> 2026-11-27 Hyperliquid 1h
(BTC/ETH/HYPE, batch-49 pinned window) results and
CALIBRATION.md for the leg-combination sensitivity checks.
