# DeMark Pivots

Tom DeMark conditional pivot breakouts, with the "day" defined as
the prior 24 bars of 1h candles.

- **X:** H+2L+C if C<O; 2H+L+C if C>O; H+L+2C if C=O (prior 24-bar
  "day" OHLC)
- **R1:** X/2 − L; **S1:** X/2 − H (one level each side — the whole
  DeMark family; classic_pivots and woodie_pivots already cover the
  multi-level families)
- **Long:** close breaks above the prior-day R1 and holds 2 bars
- **Short:** close breaks below the prior-day S1 and holds 2 bars
- **Exit:** close back inside the R1/S1 band, or the opposite level
  touched
- **Risk:** ~1.5xATR stop (≈ beyond the opposite level + 0.5xATR),
  ~3xATR target (≈ 1.5x daily range), 24-bar max hold, 1%
  risk/trade, 3x leverage — see risk.py for the ATR mapping, since
  the harness cannot express level-based stops/targets directly

Parameters: day=24 bars, hold=2 bars. WARMUP=48 (one full day +
one day for the levels to roll + margin).

Usage:

```python
from strategies.data import fetch_candles
from strategies.demark_pivots import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=365)
sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the 12 – 24 – 48 day sensitivity check.

Source: DeMark Pivot Points (Tom DeMark) —
https://www.babypips.com/learn/forex/other-pivot-point-calculation-methods

## Honest caveats

- **A daily pivot recomputed hourly is not a daily pivot.** The
  levels roll every hour, so they carry none of the auction memory
  a real daily pivot has — and the backtest says it does not work:
  combined −$12,665 on 1,420 trades, the worst of batch 37, with
  BTC at −57.8% (Sharpe −7.31, profit factor 0.43, max drawdown
  −59.2%).
- Stop and target are ATR approximations of level-based rules, not
  the exact DeMark levels (documented in risk.py).
- Single 8-month crypto window; no out-of-sample evidence.
