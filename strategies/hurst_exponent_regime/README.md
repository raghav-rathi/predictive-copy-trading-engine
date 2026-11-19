# Hurst Exponent Regime Switch

Rolling Hurst exponent (rescaled-range / R/S analysis) decides
whether the market is trending or mean-reverting, and the
strategy trades the mode it is in.

## Rules

- **Hurst:** R/S on log returns, 200-bar window, scales
  [10, 20, 40, 100]. Per scale the window is split into
  non-overlapping chunks; per chunk R = max − min of the
  mean-adjusted cumulative deviation, S = chunk std (ddof=1).
  Chunks with S or R at/below 1e-12 are skipped; H is the
  log-log slope of mean R/S vs scale. Fewer than two valid
  scales → H = 0.5. H is clipped to [0, 1].
- **Regime bands:** H > 0.55 trend, H < 0.45 reversion,
  0.45–0.55 neutral (no entries).
- **Hysteresis:** the mode changes only after 3 consecutive bars
  in the same new band; a bar in a third band restarts the
  count, a bar back in the current band clears it.
- **Trend mode:** long on EMA(20) crossing above EMA(50), short
  on a cross below. Exit on the opposite cross or a close
  through the EMA(50).
- **Reversion mode:** long on RSI(14) crossing below 30, short
  on RSI crossing above 70. Exit on RSI crossing back through 50.
- **Neutral mode:** no entries and no signal exits; the harness
  stop / trail / max hold carries the position.
- Exits are gated on the mode in force on the signal bar, so a
  trade opened in one mode is exited by that mode's rules while
  the mode persists; if the mode flips mid-trade, the new
  mode's exit rules take over.
- The harness risk layer's 2xATR stop / 2.5xATR trail also
  applies. Max hold 120 bars.
- Warmup 250 bars (200-bar Hurst window + EMA warmup).

## Sources

- DT Systems, "Market Regime Detection Trading":
  https://dtsystems.dev/blog/market-regime-detection-trading
- Nomena, "Hurst Exponent":
  https://nomena.ai/learn/hurst-exponent

## Files

- `indicators.py` — R/S Hurst estimator, hysteresis mode machine,
  EMA(20/50), RSI(14), ATR(14)
- `signals.py` — mode-gated entries/exits
- `risk.py` — batch-standard risk config, warmup 250
- `test_hurst_exponent_regime.py` — 18 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` / `CALIBRATION.md` — results and parameter notes

## How to run

From the repo root:

```
python3 -m unittest strategies.hurst_exponent_regime.test_hurst_exponent_regime -v
python3 strategies/hurst_exponent_regime/run_backtest.py
```

Paper only, no live execution.
