# Pairs Spread (BTC-ETH) — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Hedge ratio beta | Rolling 500-bar OLS slope of log(BTC) on log(ETH) | GGR's formation-period hedge ratio, made rolling and fully causal per the spec (recomputed each bar from the trailing 500 bars). 500 bars (~21 days) is long enough for a stable slope and short enough to adapt. |
| Spread | log(BTC) − beta × log(ETH) | Log-spread, the standard cointegration-style spread; beta-weighted so the two legs are in comparable units. |
| Spread instrument OHLC | BTC o/h/l/c − beta × ETH o/h/l/c (USD), volume = BTC volume | Per spec: the harness needs one OHLCV series, so the USD price spread is built with the same trailing beta at each bar. |
| z-score window | 100-bar mean / std of the log-spread | Per spec; ~4 days of history for the equilibrium band. |
| Entry thresholds | Long spread z < −2, short spread z > +2 (crosses) | GGR's canonical ±2-sigma entry. |
| Exit | z crossing back through 0 | Per spec; the spread has mean-reverted to its rolling equilibrium. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer, applied to the synthetic spread instrument's ATR. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 600 | 500-bar beta window + 100-bar z window. |

## Spec deviations

1. **Rolling beta instead of a formation-period beta.** GGR
   estimate beta once per formation period (6–12 months) and
   hold it fixed through the trading period. Here beta is
   re-estimated every bar from the trailing 500 bars, per the
   spec — a deliberate adaptation so the hedge ratio tracks the
   drifting BTC/ETH relationship on hourly data.
2. **Single spread book.** GGR trade many pairs in a portfolio.
   This batch backtests one pair as one synthetic instrument, so
   the result is a single-book number with no diversification.
3. **USD spread OHLC vs log-spread signals.** Signals use the
   log-spread z-score; the harness trades the USD price spread
   built with the same beta. The two are the same spread in
   different units; the USD version is what the ATR risk layer
   needs.
4. **No cointegration test.** GGR select pairs by historical
   cointegration / distance. BTC-ETH was specified, not selected
   — no stationarity test was run, and the backtest result
   (36 stops vs 2 signal exits) suggests the spread is not
   stationary on this window.

No bug fixes requiring re-runs, no PnL-selected tuning.
