# Dynamic Zones RSI

Adaptive overbought/oversold zones on RSI — Leo Zamansky & David
Stendahl, *Stocks & Commodities* July 1996 V15:7 (306-310).

- **RSI** = Wilder RSI(14) of close
- **Buy zone** = 12th percentile of RSI over rolling 70 bars
  ("below 88% of the sample")
- **Sell zone** = 88th percentile of RSI over rolling 70 bars
  ("above 88% of the sample")
- **Long:** RSI crosses back above the buy zone after dipping below
  it (oversold bounce)
- **Short:** RSI crosses back below the sell zone after exceeding it
  (overbought fade)
- **Exit:** RSI crosses 50 (momentum back to neutral), or touches
  the opposite zone
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 120-bar max hold
  (mean-reversion bounces need room to travel back toward 50),
  1% risk/trade, 3x leverage

The point of the zones is that they adapt: fixed 30/70 levels need
the trader to swap levels between bull and bear markets, which
negates the system's mechanical nature. The percentile zones let the
system define its own buy/sell levels from the recent RSI
distribution. Also computed (comparison only, not traded): the common
Bollinger variant — RSI mean ± 0.8σ over 20 bars — see
CALIBRATION.md.

Parameters: RSI(14), zone window 70, buy 12th / sell 88th percentile,
ATR(14) for stop/trail. WARMUP=100 (70-bar percentile zones + RSI
spin-up, with margin).

Usage:

```python
from strategies.data import fetch_candles
from strategies.dynamic_zone_rsi import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))  # 12/88 defaults
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the percentile sensitivity check and the Bollinger
variant comparison.

Sources: Dynamic Zones (Zamansky & Stendahl, S&C July 1996 V15:7) —
https://www.tradingview.com/script/AoChfBer-How-To-Use-Dynamic-Zones/
and https://docs.prorealalgos.com/dynamiczonersiup.html

## Honest caveats

- The backtest on this window is a loser on all three coins
  (combined -$12,515, PF 0.52–0.75) — see BACKTEST.md. The
  oversold-bounce entries do not pay on 1h crypto in this regime:
  RSI dips below its own 12th percentile and keeps falling, or the
  bounce dies before RSI reaches 50.
- 972 trades in 7 months is a fast pace for a "bounce" system; fees
  ($6,489) are over half the gross loss, not the whole story — the
  expectancy is negative before costs too (PF < 1 on every coin).
- The percentile zones are only as good as the last 70 bars: after a
  regime shift the zones take ~3 days to re-center, so early
  post-shift signals use stale levels.
