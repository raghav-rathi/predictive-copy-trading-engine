# Jurik RSX

RSI on Jurik's three-stage smoothing cascade — a noise-free RSI
with a fraction of the bar-to-bar jitter.

- **RSX:** public reconstruction of Jurik's RSX (length 14). Signed
  price change and absolute change each run through three cascaded
  double-EMA stages (out = 1.5a − 0.5b); RSX =
  clamp((v14/v1C + 1)·50, 0, 100), neutral 50 in a flat market
- **Long:** RSX crosses above 50 with RSX rising
- **Short:** RSX crosses below 50 with RSX falling
- **Exit:** RSX crosses back through 50, or RSX hits 80 (long) /
  20 (short)
- **Skip:** no entry if RSX is flat (|ΔRSX| < 0.5 for 3 bars)
- **Risk:** 1.5xATR stop, 2xATR target, 72-bar max hold,
  1% risk/trade, 3x leverage

Parameters: length=14, cross 50, extremes 80/20, flat filter
0.5/3 bars. WARMUP=45 (RSX warmup is length+1 = 15; the extra
margin lets the recursive cascade settle).

Usage:

```python
from strategies.data import fetch_candles
from strategies.jurik_rsx import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=365)
sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the 7 – 14 – 21 length sensitivity check.

Source: RSX (Jurik Research; Wickra docs) —
https://docs.wickra.org/Indicators/Indicator-Rsx

## Honest caveats

- **Reconstruction, not Jurik's exact code.** Jurik Research's
  RSX/JMA internals are proprietary. This implements the widely
  ported public RSX algorithm as documented by Wickra (exact
  formula in indicators.py) — values will differ from Jurik's own
  RSX, and the "three-stage smoothing cascade" label refers to
  that public reconstruction.
- The smoothing kills the whipsaw but adds lag: 50-line crosses
  confirm moves late. Backtest: combined −$7,171 on 1,030 trades,
  no coin green, expectancy −$6.96/trade vs ~$10.10/trade in fees
  — the least bad of batch 37, still a clear loser.
- Single 8-month crypto window; no out-of-sample evidence.
