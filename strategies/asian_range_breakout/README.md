# Asian Range Breakout

## Mechanism

The Asian session is typically the quiet, range-building
part of the day: low volatility, consolidation, orders
accumulating between a session high and low. The breakout
thesis is that the later, higher-volume sessions expand
out of that range, so a confirmed close beyond the Asian
range — with volume confirmation — is the day's directional
move. Adapted to 24/7 crypto, the "Asian session" is fixed
to UTC hours [0, 8).

- **Asian range:** for each UTC day, the high/low of that
  day's bars with UTC hour in [0, 8). The range is complete
  at 08:00 UTC, so no signal before 08:00 can use it.
- **Long entry:** the first 1h bar after 08:00 UTC (hour in
  [8, 16)) whose close breaks above that day's Asian range
  high AND whose volume exceeds its prior 20-bar average
  volume. At most one entry per UTC day.
- **Short entry:** mirror below the range low.
- **Exit:** the 16:00 UTC bar (end of the breakout window)
  — implemented as a signal on the hour >= 16 bar while in
  a same-day position, which the harness executes at the
  next bar's open — or the risk layer's trailing stop,
  whichever comes first. The 24-bar max hold is the
  backstop.

## Entry / exit rules

- Long entry: first post-08:00 UTC breakout above the
  Asian range high with above-average volume, while flat
  and not yet entered that UTC day.
- Short entry: mirror below the range low.
- Long exit: 16:00 UTC bar while long. Short exit mirrors.
- Risk layer: 2xATR stop, 2.5xATR trailing stop, 24-bar max
  hold, 1% risk per trade, 3x leverage cap.

## Source

Asian Session High Low Breakout Strategy (FMZ)
https://www.fmz.com/lang/en/strategy/446567

## Honest caveats

- The backtest (see BACKTEST.md) is a loser (-$1,186 over
  500 trades, combined Sharpe -0.50). Only ETH is green;
  BTC and HYPE both lose. The 24/7 crypto "Asian range"
  does not behave like the FX session range the idea comes
  from — crypto has no real session close, so the range is
  an arbitrary 8-hour window.
- 326 of 500 exits are time exits (the 16:00 close), so
  most trades are simply held to the window end whether
  they are winning or not.
- Paper/backtest only. Nothing here touches live execution.
