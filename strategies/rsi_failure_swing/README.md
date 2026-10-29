# RSI Failure Swing

## Mechanism

A failure swing is Wilder's RSI-only turn pattern, as systematized
in Cardwell's RSI range rules. It reads momentum exhaustion
directly off the oscillator, with no price comparison at all —
that is the whole difference from `rsi_divergence`, which needs
price and RSI to disagree at pivot extremes. Here price is never
consulted:

- **RSI(14):** Wilder's construction (the `rsi` primitive in
  `strategies/base.py`).
- **Bullish failure swing:** RSI dips below 30, rallies to a
  swing high, pulls back to a HIGHER swing low, then breaks
  above that intervening swing high. The second low "fails" to
  reach the first: downside momentum is spent even if price is
  still making lower lows.
- **Bearish failure swing:** mirror — RSI tops above 70, falls
  to a swing low, rallies to a LOWER swing high, then breaks
  below that intervening swing low.
- **Pivots:** a swing extreme centered at bar j is only usable
  from bar j+2 (it must be the extreme over bars j−2..j+2), so
  the trigger never reads unconfirmed data. Same-kind pivots
  are kept strictly alternating: a deeper low replaces the
  previous low rather than appending a second one.

## Entry / exit rules

- Long entry: bullish failure-swing trigger bar while flat.
- Short entry: bearish failure-swing trigger bar while flat.
- Long exit: a bearish failure-swing bar while long. Short exit
  mirrors.
- Risk layer: 2xATR stop, 2.5xATR trailing stop, 168-bar max
  hold, 1% risk per trade, 3x leverage cap.

## Source

RSI failure swings (Wilder; Cardwell RSI range rules) —
StockCharts ChartSchool
https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/relative-strength-index-rsi

## Honest caveats

- The backtest (see BACKTEST.md) loses on all three coins
  (-$2,310 over 100 trades, worst leg BTC -$1,187 at a 21.2%
  win rate). The stop dominates exits (94 of 100 trades):
  RSI breaking its own swing extreme on 1h crypto is usually
  a continuation print, not a turn.
- The trigger window is narrow: once RSI prints a new pivot
  past the pattern, the setup evaporates, so many patterns
  never trigger at all — only 100 trades in 7 months across
  three coins.
- Paper/backtest only. Nothing here touches live execution.
