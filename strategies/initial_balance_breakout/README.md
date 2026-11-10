# Initial Balance Breakout

Market Profile Initial Balance breakout (J. Peter Steidlmayer, CBOT, 1980s), adapted to 24/7 crypto on 1h bars with the UTC day as the session. The Initial Balance is the high/low of the first hour of the day (the 00:00–01:00 UTC bar); it stays fixed all day and defines the day's key levels.

## Rules

- Long: the first bar after the IB bar (01:00–13:00 UTC) whose close is above the IB high. Short: the first bar after the IB bar whose close is below the IB low. First side broken wins; one trade per UTC day.
- Exit a long on a close back below the IB high (reclaim = idea wrong) or on a close at/above the 1x IB extension target (IB high + IB range). Exit a short on a close back above the IB low or on a close at/below IB low − IB range.
- A 2.0x ATR stop with a 2.5x ATR chandelier trail also applies (the book's far-side-of-IB stop is replaced by the batch-standard ATR stop; see CALIBRATION.md). Max hold 23 bars.
- All computation is causal, so signals on bar i use only data through bar i's close.

## Source

- J. Peter Steidlmayer, *Market Profile* (CBOT, 1980s)
- Initial Balance breakout explainer: https://www.loomiai.io/learn/initial-balance-breakout-strategy/
- Initial Balance breakout backtest (NQ): https://ripbacktest.com/posts/initial-balance-breakout-strategy-nq/

Paper only, no live execution.
