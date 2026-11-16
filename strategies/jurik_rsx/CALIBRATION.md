# Jurik RSX — Calibration

Length sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-11-16, same costs/sizing, 1.5xATR
stop, 2xATR target, 72-bar max hold). The sweep re-runs
`add_indicators(df, length=L)` only — signals and risk are
unchanged.

| Length | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 7 | BTC | 680 | 36.6% | -$7,833 | -7.99 | 0.57 | -$11.52 |
| 7 | ETH | 688 | 37.1% | -$6,415 | -5.15 | 0.68 | -$9.32 |
| 7 | HYPE | 664 | 40.2% | -$4,587 | -3.10 | 0.78 | -$6.91 |
| 14 (shipped) | BTC | 339 | 42.8% | -$1,787 | -0.97 | 0.90 | -$5.27 |
| 14 (shipped) | ETH | 355 | 38.3% | -$3,825 | -2.77 | 0.78 | -$10.78 |
| 14 (shipped) | HYPE | 336 | 41.1% | -$1,558 | -0.87 | 0.90 | -$4.64 |
| 21 | BTC | 221 | 43.4% | -$1,485 | -0.95 | 0.88 | -$6.72 |
| 21 | ETH | 240 | 42.9% | -$1,339 | -0.92 | 0.90 | -$5.58 |
| 21 | HYPE | 230 | 40.9% | -$2,130 | -1.59 | 0.84 | -$9.26 |

## One-line verdict

- **7:** the chop setting — 664–688 trades per coin, combined
  -$18,835, Sharpe -3.10 to -7.99. A length-7 RSX is barely
  smoother than RSI and crosses 50 on noise.
- **21:** least bad combined (-$4,955) with the best win rates of
  the sweep (40.9–43.4%) — but still red on all three coins, and
  the improvement is mostly fewer trades (691 vs 1,030), i.e. a
  smaller fee bill, not a better signal.
- **14 (shipped):** middle of the pack combined (-$7,171); the
  only setting with profit factors at 0.90 on two coins — and that
  is an in-sample observation, not a justification.
- **Shipped decision:** keep the specified length 14 as the
  registry config regardless. The length 14 was fixed before any
  backtest was run; the in-sample ranking does not change that, and
  leaning toward 21 *because* it loses less would be in-sample
  selection on a window where no setting works on any coin. The
  honest read: the length moves the trade count and the lag, not
  whether a smoothed 50-line cross has edge — on this window it
  does not, at any length.
