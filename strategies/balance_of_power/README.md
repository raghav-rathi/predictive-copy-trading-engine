# Balance of Power

Buyer-vs-seller control gauge (Igor Livshin, *Stocks & Commodities*,
August 2001).

## Mechanism

Each bar answers one question: **who won this bar?**

- **Raw BOP** = (close − open) / (high − low) — where the close landed
  inside the bar's range, normalized. +1 = opened at the low and
  closed at the high (buyers owned the whole bar); −1 = the reverse
  (sellers owned it). A degenerate flat bar (high == low) reads 0.0.
- **BOP** = SMA(raw BOP, 14) — the smoothed control line. Sustained
  positive = buyers in control (up-trend regime); sustained negative
  = sellers in control.

The zero line is the regime threshold. A cross through it means
**control just changed hands**, and tops/tends cluster: in bull
markets BOP readings press up toward +1 as buyers dominate bar after
bar, in bear markets they cluster near −1.

## Rules

- **Long:** smoothed BOP crosses above 0 (buyers take control)
- **Short:** smoothed BOP crosses below 0 (sellers take control)
- **Exit:** the opposite zero-cross — once control flips back, the
  thesis is gone
- **Risk:** 2xATR hard stop, 2.5xATR chandelier trail, 150-bar max
  hold (regime legs can persist), 1% risk/trade, 3x leverage

Parameters: SMA len=14 (shipped), ATR(14) for stop/trail. WARMUP=30
(SMA spin-up plus margin).

Usage:

```python
from strategies.data import fetch_candles
from strategies.balance_of_power import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))  # n=14 default
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the n=7/14/28 sensitivity check.

Source: Balance of Power (Igor Livshin, S&C Aug 2001) —
https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/balance-of-power-bop.md
