# Markov Regime Switching — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| States | 2 (calm low-vol, turbulent high-vol) | Hamilton's canonical 2-state regime model; the spec fixes two states. |
| Emission | Gaussian per state on 1h log returns | Hamilton (1989) verbatim: each regime is a Gaussian with its own mean and variance. |
| EM iterations | 25 | Per spec; forward-backward EM converges well inside 25 iterations on 1000 points (loglik stabilises). |
| EM init | Split at median \|return\| into low/high groups; each state's (mu, sigma) starts at its group's moments; A = [[0.95, 0.05], [0.05, 0.95]], pi = [0.5, 0.5] | Deterministic, volatility-driven initialisation: it seeds the split the model is meant to find (variance regimes) instead of a random start. |
| Calibration window | First 1000 log returns per coin, fit once, never refit | Per spec: the in-sample calibration window. Parameters are frozen after it; later bars are classified only by the causal forward filter. |
| Regime rule | Turbulent when forward-filtered P(turbulent) > 0.5 | Standard MAP classification from the filter. |
| Calm system | EMA(12)/EMA(26) cross | Per spec; the textbook fast/slow trend pair. |
| Turbulent system | RSI(14): long on cross up through 30, short on cross down through 70, exit at 50 | Per spec; the canonical oversold/overbought mean-reversion levels. |
| Exits | Either system's exit closes a position in either regime | Per spec: "exits = opposite regime-system exit or the other system's exit". |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 1100 | 1000-bar calibration + 100-bar filter burn-in, per spec. |

## Spec deviations

1. **No smoothing, filter only after calibration.** Hamilton's
   smoother uses the full sample; the shipped code uses the
   causal forward filter for every bar's regime (the smoother is
   used only inside EM on the calibration window). This is the
   only lookahead-free way to classify live bars.
2. **Frozen fit.** The HMM is fit once and never refit, per the
   spec. A rolling refit would be the natural production choice
   but would change the documented calibration design.
3. **Sigma floor 1e-6.** A degenerate constant-return window
   would give sigma 0 and a division by zero; the floor keeps the
   fit defined (returns 0 rather than NaN) with no effect on real
   data.
4. **pi collapses to a corner.** On BTC/ETH the fitted pi is
   [0.0, 1.0] (first return assigned to the turbulent state) and
   on HYPE [1.0, 0.0]. pi only affects the first bar's filter, so
   this is cosmetic — but it is reported as fitted, not smoothed
   over.

No bug fixes requiring re-runs, no PnL-selected tuning.
