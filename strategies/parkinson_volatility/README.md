# Parkinson Volatility Expansion

Parkinson (1980) realized volatility: the range of a bar
carries more information about its variance than the close
alone. When realized volatility expands above its slow
baseline, trade the expansion in the direction of the
EMA(20) trend.

- **Parkinson variance (per bar):** v = ln(H/L)^2 / (4*ln2).
  Range-only: no open/close term, so no clip is needed
  (the term is always >= 0).
- **pk_vol:** sqrt(rolling mean of v over 20 bars)
- **pk_vol_sma:** SMA(pk_vol, 60) -- the slow volatility
  baseline
- **ema20:** EMA(close, 20) -- trend direction filter
- **Long:** pk_vol crosses ABOVE pk_vol_sma AND close > ema20
- **Short:** pk_vol crosses ABOVE pk_vol_sma AND close < ema20
- **Exit:** pk_vol crosses back BELOW pk_vol_sma (volatility
  contraction ends either side's trade), or the close crosses
  the wrong side of EMA(20). 2xATR hard stop, 3xATR trail,
  72-bar max hold behind them.
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 72-bar
  max hold, 1% risk/trade, 3x leverage

Parameters: vol window 20 bars, vol-SMA length 60 bars,
EMA(20), ATR(14) for risk. Entries are CROSS-based
(crossed_above on pk_vol vs pk_vol_sma), never level
conditions -- a level condition would re-fire every bar
volatility sat above its baseline. The EMA(20) filter is a
level condition on the close, but it only gates the
cross-based vol trigger; it never fires an entry on its own.

Deviations / implementation notes (all documented, none
tuned to PnL):

- The vol cross is the entry trigger; the close-vs-EMA20
  test is a same-bar gate, not a cross. Requiring a fresh
  EMA cross as well would be a different (stricter) strategy.
- A volatility contraction (cross below the SMA) exits both
  sides: the setup is "volatility is expanding", and once it
  stops expanding the trade is over regardless of direction.
- Parkinson's estimator ignores the open/close drift term
  that Garman-Klass includes; that is the point of the
  estimator, not a simplification. On trending bars it
  overstates variance relative to GK; on reversal bars it
  understates it.

Sources: Parkinson (1980), "The Extreme Value Method for
Estimating the Variance of the Rate of Return" --
https://kaisquant.com/posts/range-volatility-estimators/

Sibling: garman_klass_volatility uses the identical trade
structure with the Garman-Klass estimator in place of
Parkinson; see its BACKTEST.md for the head-to-head
comparison.

Usage:

```python
from strategies.parkinson_volatility import indicators, signals, risk

df = indicators.add_indicators(df)  # vol_window=20, vol_sma=60 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 -> 2026-11-27 Hyperliquid 1h
(BTC/ETH/HYPE, batch-49 pinned window) results and
CALIBRATION.md for the vol-window (10/20/40) and vol-SMA
(30/60/120) sensitivity checks.
