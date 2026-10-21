# Woodies CCI

Ken Wood's CCI system — the mechanical Zero-Line Reject pattern.
Two CCIs run side by side: CCI(14) is the trend line (which side of
the zero line it holds defines the tradeable direction), and the
fast CCI(6) "turbo" is the trigger. The entry is a with-trend
pullback: the trend line tags toward the zero line without crossing
it, and the turbo hooking back through zero times the re-entry.

- **Long:** CCI(14) above zero for 6+ consecutive bars AND pulled
  back into [0, 50], while CCI(6) crosses back above zero
- **Short:** CCI(14) below zero for 6+ consecutive bars AND pulled
  back into [-50, 0], while CCI(6) crosses back below zero
- **Exit:** CCI(14) crosses the zero line (the premise is gone)
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 60-bar max hold,
  1% risk/trade, 3x leverage

Parameters: trend CCI(14), turbo CCI(6), trend qualifier 6 bars,
pullback zone 50, ATR(14) for stop/trail.

Usage:

```python
from strategies.data import fetch_candles
from strategies.woodies_cci import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=240)
sig = signals.add_signals(indicators.add_indicators(df))  # trend_bars=6 default
```

See BACKTEST.md for the 2026-03-14 → 2026-10-21 Hyperliquid 1h
(BTC/ETH/HYPE) results — honest verdict: loser on all three coins,
~zero edge gross of fees — and CALIBRATION.md for the 4/6/9
trend-qualifier sensitivity check.
