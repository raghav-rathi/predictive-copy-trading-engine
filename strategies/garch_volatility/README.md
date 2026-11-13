# GARCH Volatility

Bollerslev (1986) GARCH(1,1) volatility-regime trend system: forecast
variance on 1h log returns, and trade 20-bar breakouts only when the
forecast volatility sits in its normal regime — not in a panic spike,
not in a dead calm.

## Rules

- Forecast variance: `sigma2_t = omega + alpha*r_{t-1}^2 +
  beta*sigma2_{t-1}` with fixed omega=1e-8, alpha=0.08, beta=0.90,
  seeded at the unconditional variance omega/(1-alpha-beta) = 5e-7.
  No MLE fitting, no PnL tuning.
- Regime: forecast vol vs its trailing 1000-bar percentiles. NORMAL
  band = 30th–70th percentile.
- **Long entry:** close crosses above the previous 20-bar high AND
  forecast vol is inside the normal band.
- **Short entry:** close crosses below the previous 20-bar low AND
  forecast vol is inside the normal band.
- **Long exit:** close falls back below the previous 20-bar high
  (back inside the 20-bar range).
- **Short exit:** close rises back above the previous 20-bar low.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 1100 bars (1000-bar percentile window + margin).

All computation is causal, so signals on bar i use only data through
bar i's close (the forecast vol itself only through bar i-1).

## Source

- Tim Bollerslev, "Generalized Autoregressive Conditional
  Heteroskedasticity", *Journal of Econometrics* 31(3), 1986:
  https://en.wikipedia.org/wiki/Autoregressive_conditional_heteroskedasticity

Paper only, no live execution.
