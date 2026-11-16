# Bayesian Changepoint

Adams & MacKay Bayesian online changepoint detection on log-returns;
trade the direction of the post-change mean return.

- **Model:** Gaussian likelihood, Normal-Inverse-Gamma conjugate prior
  (mu0=0, kappa0=5, alpha0=1, beta0=1e-4), constant hazard 1/100,
  run length capped at 200
- **Long:** changepoint detected (P(change) > 0.5) and post-change
  mean return > 0
- **Short:** changepoint detected and post-change mean return < 0
- **Exit:** next changepoint, or post-change mean flips sign
- **Risk:** 1.5xATR stop, 72-bar max hold, no target, 1% risk/trade,
  3x leverage

Parameters: hazard=0.01, RMAX=200. WARMUP=50 (BOCD spin-up).

Usage:

```python
from strategies.data import fetch_candles
from strategies.bayesian_changepoint import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=365)
sig = signals.add_signals(indicators.add_indicators(df))  # hazard=0.01 default
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the hazard 0.005 – 0.01 – 0.02 sensitivity check.

Source: Bayesian Online Changepoint Detection (Adams & MacKay 2007) —
https://arxiv.org/pdf/0710.3742

## Honest caveats

- The detector fires on volatility-only shifts too, not just mean
  shifts — and the backtest shows it: BTC win rate 19%, ETH 14%.
  The post-change mean sign right after a changepoint is estimated
  from a handful of bars and is mostly noise.
- The HYPE leg (+$1,109, Sharpe +1.45) is 5 trades; do not read it
  as a winner. Combined the strategy is -$403 on 55 trades.
- Prior note: kappa0=5 (not 1) is load-bearing — with a very weak
  mean prior the posterior keeps a ~1% atom at run length 0 whose
  prior-predictive density explains a genuine mean shift almost as
  well as a changepoint does, so P(change) peaks near 0.43 on an
  8-sigma shift and the 0.5 threshold never fires. See
  `indicators.py`.
- Single 8-month crypto window; no out-of-sample evidence.
