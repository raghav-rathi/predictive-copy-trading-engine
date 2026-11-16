# ARMS Index (TRIN) — Calibration

TRIN-window sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-11-16, same
costs/sizing, 1.5xATR stop, 2xATR target, 24-bar max hold). The
sweep re-runs `add_indicators(df, window=W)` only — signals and
risk are unchanged.

| Window | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 5 | BTC | 724 | 40.6% | -$6,991 | -5.65 | 0.66 | -$9.66 |
| 5 | ETH | 728 | 46.7% | -$1,805 | -0.78 | 0.93 | -$2.48 |
| 5 | HYPE | 667 | 44.8% | -$3,643 | -2.10 | 0.85 | -$5.46 |
| 10 (shipped) | BTC | 458 | 41.7% | -$4,311 | -3.08 | 0.76 | -$9.41 |
| 10 (shipped) | ETH | 451 | 39.9% | -$3,627 | -2.23 | 0.76 | -$8.04 |
| 10 (shipped) | HYPE | 390 | 43.8% | -$3,303 | -2.48 | 0.80 | -$8.47 |
| 20 | BTC | 160 | 41.2% | -$2,035 | -2.05 | 0.73 | -$12.72 |
| 20 | ETH | 195 | 44.1% | -$1,783 | -1.56 | 0.79 | -$9.14 |
| 20 | HYPE | 110 | 48.2% | +$665 | +0.73 | 1.11 | +$6.04 |

## One-line verdict

- **5:** the churn setting — 667–728 trades per coin, combined
  -$12,440. A 5-bar TRIN flips levels on noise; BTC alone loses
  -$6,991 at Sharpe -5.65.
- **20:** least bad combined (-$3,153) and the only setting with a
  green coin (HYPE +$665, Sharpe +0.73, PF 1.11) — but BTC and ETH
  still lose -$2,035 / -$1,783, and the improvement comes mostly
  from trading one-third as often (465 vs 1,299 trades), i.e. from
  paying one-third the fees, not from a better signal.
- **10 (shipped):** worst combined (-$11,241) of the three — and
  that is an in-sample observation, not a justification.
- **Shipped decision:** keep the specified 10-bar window as the
  registry config regardless. The 10-bar window was fixed before
  any backtest was run; the in-sample ranking does not change that,
  and leaning toward 20 *because* it loses less would be in-sample
  selection on a window where no setting works on all three coins.
  The honest read: the window moves the trade count and the fee
  bill, not whether the single-asset TRIN proxy works — it does
  not, at any window.
