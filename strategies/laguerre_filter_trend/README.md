# Laguerre Filter Trend

Trend entries on John Ehlers' four-element Laguerre filter
("Time Warp, Without Space Travel"), gamma=0.8, applied to
hl2 = (h+l)/2.

- **Recursion:** L0=(1−γ)·x+γ·L0[1]; L1=−γ·L0+L0[1]+γ·L1[1];
  L2=−γ·L1+L1[1]+γ·L2[1]; L3=−γ·L2+L2[1]+γ·L3[1]
- **Filter:** Filt = (L0 + 2·L1 + 2·L2 + L3) / 6
- **Long:** close crosses above Filt and Filt is rising
- **Short:** close crosses below Filt and Filt is falling
- **Exit:** the opposite price/filter cross
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 200-bar max hold,
  1% risk/trade, 3x leverage

Parameters: gamma=0.8, ATR(14) for stop/trail. WARMUP=60 (filter state
settles within tens of bars; margin included).

Usage:

```python
from strategies.data import fetch_candles
from strategies.laguerre_filter_trend import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))  # gamma=0.8 default
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the gamma=0.5/0.8/0.9 sensitivity check.

Sources:
- https://efs.kb.esignal.com/hc/en-us/articles/6362941110555-Four-Element-Laguerre-Filter-by-John-Ehlers
- https://www.luxalgo.com/library/concept/laguerre-filter/

## Honest caveats

- **This strategy loses badly on every coin in the batch window**
  (combined -$6,462, win rate 17.7%). The filter tracks price so
  closely that price crosses it constantly in chop: 204–258 exit
  crosses per coin vs only 69–98 entries, and 96–138 of ~143–190
  trades exit on the signal — i.e. positions are whipsawed out almost
  immediately. The slope condition (filter rising/falling) does not
  save it; the filter's slope flips with price.
- The 15–20% win rate with PF 0.45–0.72 means winners are rare and
  small relative to losers; the 2xATR stop fires on only ~1/3 of
  trades because the signal exit usually fires first.
- Gamma=0.9 is the only setting with any green coin (HYPE +$854) and
  it is still combined-negative; do not tune gamma to chase it.
- Single 7-month crypto window; no out-of-sample evidence.
