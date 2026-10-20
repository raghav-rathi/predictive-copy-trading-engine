# OU Half-Life Z-Score Mean Reversion

A mean-reversion engine that estimates the **Ornstein–Uhlenbeck
half-life** of log-price deviations causally, every bar, and only
trades when the estimated reversion speed is in a sane band.

## Mechanism

1. **Deviation**: `dev = log(close) − SMA(log(close), 50)`.
2. **Per-bar AR(1) fit**: regress `dev.diff()` on `dev.shift(1)` over
   the trailing 100 dev values, vectorized with rolling covariance /
   variance (`θ = cov/v ar`, fully causal, O(n)).
3. **Half-life**: `HL = −ln(2)/θ`. A bar is tradable only when
   `θ < 0` (mean-reverting) and `5 ≤ HL ≤ 120` — explosive and
   near-unit-root regimes are excluded.
4. **Z-score**: `z = dev / rolling_std(dev, 50)`.
5. **Entry**: long when `z < −2` and HL valid; short when `z > 2`
   and HL valid.
6. **Exits**: long exits when `z ≥ 0`, short when `z ≤ 0`. The risk
   config adds a 2.5xATR hard stop (deviations stretch) and a
   200-bar max hold (half-life estimates go stale).

## Parameters

| Param | Value |
|---|---|
| Deviation SMA | 50 bars (log prices) |
| AR(1) window | 100 bars |
| Z-score std span | 50 bars |
| Entry z | ±2.0 |
| HL validity band | 5–120 bars |
| Stop | 2.5 × ATR(14), no target, no trail |
| Max hold | 200 bars |
| Sizing | 1% risk/trade, 3× leverage cap |

## Usage

```python
from strategies.ou_zscore import indicators, risk, signals

ind = indicators.add_indicators(df)   # OHLCV with t,o,h,l,c,v
sig = signals.add_signals(ind)
from strategies.backtest import run_backtest
res = run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                   use_funding=False)
print(res.metrics())
```

## Source

OU half-life mean reversion —
https://www.luxalgo.com/blog/mean-reversion-strategies-for-algorithmic-trading/
