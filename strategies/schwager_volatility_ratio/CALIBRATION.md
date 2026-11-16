# Schwager Volatility Ratio — Calibration

VR-threshold sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-11-16, same
costs/sizing, 2xATR stop, 3xATR target, 10-bar max hold). The sweep
re-runs `add_signals(df, vr_thresh=V)` only — indicators and risk
are unchanged.

| VR thresh | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 1.5 | BTC | 365 | 46.8% | -$3,733 | -2.94 | 0.76 | -$10.23 |
| 1.5 | ETH | 319 | 47.0% | -$3,226 | -2.58 | 0.75 | -$10.11 |
| 1.5 | HYPE | 342 | 44.4% | -$4,069 | -3.63 | 0.66 | -$11.90 |
| 2.0 (shipped) | BTC | 191 | 42.9% | -$3,595 | -3.77 | 0.59 | -$18.82 |
| 2.0 (shipped) | ETH | 186 | 43.0% | -$3,186 | -3.19 | 0.62 | -$17.13 |
| 2.0 (shipped) | HYPE | 138 | 42.8% | -$2,030 | -2.38 | 0.66 | -$14.71 |
| 2.5 | BTC | 107 | 41.1% | -$2,050 | -2.51 | 0.62 | -$19.16 |
| 2.5 | ETH | 104 | 45.2% | -$1,700 | -1.96 | 0.68 | -$16.34 |
| 2.5 | HYPE | 58 | 41.4% | -$1,454 | -2.48 | 0.50 | -$25.08 |

## One-line verdict

- **1.5:** the most trades (1,026) and the worst combined (-$11,027).
  A looser threshold admits more continuation bars as fades; the win
  rate rises to ~47% but the expectancy stays near -$10/trade.
- **2.5:** the least bad combined (-$5,204) — but only by trading
  less (269 trades) while the per-trade expectancy gets *worse*
  (-$19.16 on BTC, -$25.08 on HYPE). The threshold filters volume,
  not quality.
- **2.0 (shipped):** middle of the road (-$8,810, 515 trades); every
  coin red at every threshold, Sharpe below -1.9 everywhere.
- **Shipped decision:** keep the specified VR > 2.0 regardless. The
  2.0 threshold was fixed before any backtest was run; leaning toward
  2.5 *because* it loses less would be in-sample selection on a
  window where the fade loses at every setting. The honest read: the
  threshold moves how often the fade fires, not whether fading wide
  bars pays — on this window it does not.
