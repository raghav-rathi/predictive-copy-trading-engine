# Prior Day High/Low Breakout — Calibration

Breakout-filter sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-11-16, same
costs/sizing, range filter 0.5x 20-day median, 1.5xATR stop, 3xATR
target, 24-bar max hold). The sweep re-runs
`add_signals(df, filt=F)` only — indicators and risk are unchanged.

| Filter | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 0.05% | BTC | 211 | 27.5% | -$3,222 | -2.71 | 0.65 | -$15.27 |
| 0.05% | ETH | 183 | 29.0% | -$2,203 | -1.86 | 0.76 | -$12.04 |
| 0.05% | HYPE | 247 | 28.3% | -$2,204 | -1.83 | 0.80 | -$8.92 |
| 0.1% (shipped) | BTC | 202 | 29.2% | -$3,348 | -2.80 | 0.63 | -$16.57 |
| 0.1% (shipped) | ETH | 171 | 30.4% | -$1,789 | -1.46 | 0.80 | -$10.46 |
| 0.1% (shipped) | HYPE | 231 | 29.4% | -$1,910 | -1.56 | 0.82 | -$8.27 |
| 0.2% | BTC | 184 | 30.4% | -$3,652 | -3.14 | 0.57 | -$19.85 |
| 0.2% | ETH | 158 | 31.6% | -$2,193 | -1.89 | 0.74 | -$13.88 |
| 0.2% | HYPE | 219 | 30.6% | -$1,935 | -1.61 | 0.81 | -$8.83 |

## One-line verdict

- **0.05%:** combined -$7,629 on 641 trades — the loosest filter
  fires most and loses most; win rates fall to 27.5–29.0%.
- **0.2%:** combined -$7,780 on 561 trades — the strictest filter
  fires least and still loses most; BTC gets worse (-$3,652,
  Sharpe -3.14) as the filter delays entries into already-failed
  breakouts.
- **0.1% (shipped):** least bad combined (-$7,046) — but least bad
  among three losers is not a recommendation; every coin is red at
  every filter.
- **Shipped decision:** keep the specified 0.1% filter regardless.
  The 0.1% filter was fixed before any backtest was run; the
  in-sample ranking does not change that, and leaning toward 0.1%
  *because* it is least bad would be in-sample selection on a window
  where no setting works on any coin. The honest read: the filter
  moves how often the breakout fires, not whether the level means
  anything — on this window it does not.
