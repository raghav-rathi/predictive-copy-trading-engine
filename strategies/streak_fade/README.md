# Consecutive Days Fade (Connors)

Larry Connors' consecutive-days finding (TradingMarkets,
2007; 7M+ trades, 1995-2006): stocks closing up 3+
consecutive days underperform, and the underperformance
grows with the streak; stocks closing down 3+ consecutive
days outperform, growing with the streak. This engine fades
the streak on 1h crypto bars: short the 4th consecutive up
close, long the 4th consecutive down close, and exit when
the close reverts through its 10-bar mean.

- **up_streak:** count of consecutive closes above the prior
  close; resets to 0 on a down/flat close
- **down_streak:** count of consecutive closes below the
  prior close; resets to 0 on an up/flat close
- **SHORT:** up_streak crosses above 3 (the 4th consecutive
  up close -- fires exactly once per streak)
- **LONG:** down_streak crosses above 3 (the 4th consecutive
  down close)
- **Exit:** long exits when the close crosses ABOVE SMA(10)
  (reversion to the mean); short exits when the close crosses
  BELOW SMA(10); or the opposite entry fires. 2xATR hard stop,
  3xATR trail, 24-bar max hold behind them.
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 24-bar
  max hold, 1% risk/trade, 3x leverage

Parameters: streak threshold 4 closes, exit SMA(10),
ATR(14) for risk. Entries are CROSS-based
(crossed_above on the streak count), never level
conditions -- a level condition such as up_streak >= 4
would re-fire every bar a long streak persisted.

Deviations / implementation notes (all documented, none
tuned to PnL):

- Connors' study is on daily stock closes; this engine
  applies the same streak logic to 1h crypto closes, per
  the brief. The streak-length finding (underperformance
  grows with the streak) is the reason the shipped
  threshold is 4 rather than 3: CALIBRATION.md sweeps 3/4/5.
- A flat close resets both streaks (neither up nor down).
- The exit is a close crossing SMA(10), not the streak
  reversing: a streak can end (one down close after four
  up closes) while price stays well above its mean, and
  the fade is only proven wrong -- or right -- at the mean.

Sources: Larry Connors, "Consecutive Up/Down Days" --
https://tradingmarkets.com/recent/if_a_stock_drops_5_days_in_a_row_should_you_buy_it-674228

Usage:

```python
from strategies.streak_fade import indicators, signals, risk

df = indicators.add_indicators(df)  # streak_n=4, sma_n=10 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 -> 2026-11-27 Hyperliquid 1h
(BTC/ETH/HYPE, batch-49 pinned window) results and
CALIBRATION.md for the streak-threshold (3/4/5) and exit-SMA
(5/10/20) sensitivity checks.
