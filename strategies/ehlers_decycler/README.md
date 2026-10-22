# Decycler Trend

Trend-following entries on John Ehlers' Decycler (TASC, September
2015) — a trend extractor built from a 2-pole Butterworth high-pass
filter rather than moving averages.

## Mechanism

A high-pass filter strips fast cycles out of price; subtracting the
cyclic component from the close leaves the trend component:

- **w** = 0.707 × 2π / P  (P = cutoff period, shipped P=20)
- **alpha** = (cos w + sin w − 1) / cos w
- **hp[i]** = (1 − alpha/2)² × (p[i] − 2·p[i−1] + p[i−2])
  + 2(1−alpha)·hp[i−1] − (1−alpha)²·hp[i−2],  hp[0..1] = 0
- **decycler** = close − hp

Cycles shorter than the cutoff period pass through the high-pass and
are removed; slower components stay in the decycler line, which has
no lag of its own — the only "smoothing" is the cutoff, not a moving
average. Caveat: the Butterworth's phase shift means cycles near the
cutoff only attenuate, they do not cancel fully (a period-5 sine at
P=20 leaves ~30% residual).

## Rules

- **Long:** close crosses above the decycler while the decycler is
  rising (trend component moving with the trade)
- **Short:** close crosses below the decycler while it is falling
- **Exit:** the opposite cross — once the trend component turns the
  other way, the position's premise is gone
- **Risk:** 2xATR hard stop, 2xATR chandelier trail, 150-bar max hold,
  1% risk/trade, 3x leverage

Parameters: cutoff P=20, ATR(14) for stop/trail. WARMUP=80 (filter
spin-up + ATR spin-up, with margin).

Usage:

```python
from strategies.data import fetch_candles
from strategies.ehlers_decycler import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))  # period=20 default
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the P=10/20/40 sensitivity check.

Source: Decycler (John Ehlers, TASC Sep 2015) —
https://ar.tradingview.com/scripts/ehlers/
