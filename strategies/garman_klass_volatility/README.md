# Garman-Klass Volatility Expansion

Garman & Klass (1980) realized volatility: the range of a bar
carries more information about its variance than the close
alone. When realized volatility expands above its slow
baseline, trade the expansion in the direction of the
EMA(20) trend.

- **GK variance (per bar):** v = 0.5 * ln(H/L)^2 -
  (2*ln2 - 1) * ln(C/O)^2, clipped at >= 0 per bar (before
  averaging). The open/close term corrects the range term
  for drift; the clip keeps the estimate non-negative.
- **gk_vol:** sqrt(rolling mean of v over 20 bars)
- **gk_vol_sma:** SMA(gk_vol, 60) -- the slow volatility
  baseline
- **ema20:** EMA(close, 20) -- trend direction filter
- **Long:** gk_vol crosses ABOVE gk_vol_sma AND close > ema20
- **Short:** gk_vol crosses ABOVE gk_vol_sma AND close < ema20
- **Exit:** gk_vol crosses back BELOW gk_vol_sma (volatility
  contraction ends either side's trade), or the close crosses
  the wrong side of EMA(20). 2xATR hard stop, 3xATR trail,
  72-bar max hold behind them.
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 72-bar
  max hold, 1% risk/trade, 3x leverage

Parameters: vol window 20 bars, vol-SMA length 60 bars,
EMA(20), ATR(14) for risk. Entries are CROSS-based
(crossed_above on gk_vol vs gk_vol_sma), never level
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
- The per-bar GK term is clipped at zero BEFORE the 20-bar
  average, per the brief; clipping the average instead would
  let negative bars drag the estimate and is not the
  Garman-Klass construction.

Sources: Garman & Klass (1980), "On the Estimation of
Security Price Volatilities from Historical Data" --
https://kaisquant.com/posts/range-volatility-estimators/

Sibling: parkinson_volatility uses the identical trade
structure with the Parkinson (1980) range-only estimator
in place of Garman-Klass; see its BACKTEST.md for the
head-to-head comparison.

Usage:

```python
from strategies.garman_klass_volatility import indicators, signals, risk

df = indicators.add_indicators(df)  # vol_window=20, vol_sma=60 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 -> 2026-11-27 Hyperliquid 1h
(BTC/ETH/HYPE, batch-49 pinned window) results and
CALIBRATION.md for the vol-window (10/20/40) and vol-SMA
(30/60/120) sensitivity checks.
