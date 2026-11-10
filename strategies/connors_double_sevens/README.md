# Connors Double 7s

Larry Connors & Cesar Alvarez's Double 7s mean-reversion system, from
*Short Term Trading Strategies That Work*: buy a market in an uptrend
when it makes its lowest close in 7 days, and sell when it makes its
highest close in 7 days. "Days" are UTC calendar days; the 1h frame
is resampled to daily closes, the signal is evaluated on the day's
last bar (23:00 UTC), and the harness enters at the next bar's open —
the causal equivalent of buying on the close.

## Rules

- Long entry: the daily close is the lowest daily close of the last 7
  days (including today) AND the daily close is above the 200-day SMA
  of daily closes.
- Long exit: the daily close is the highest daily close of the last 7
  days (including today).
- Long-only — no shorts.
- No stop loss, no target: the 7-day-high close is the only exit in
  the original system. (The harness carries a 10x ATR stop as a
  formality; in the backtest it fired on 4 of 10 exits — see
  BACKTEST.md.)
- All computation is causal, so signals on bar i use only data
  through bar i's close.

## Source

- Larry Connors & Cesar Alvarez, *Short Term Trading Strategies That
  Work* (Double 7s)
- https://sacredtraders.com/three-rules-one-easy-way-to-trade-etfs-by-larry-connors-and-david-penn/
- https://thealgobench.com/strategies/double-seven/

Paper only, no live execution.
