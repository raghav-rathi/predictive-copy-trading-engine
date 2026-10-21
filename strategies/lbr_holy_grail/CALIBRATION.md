# Holy Grail — Calibration

ADX entry-threshold sensitivity, same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-21, same costs/sizing,
2xATR stop, 3xATR trail, 100-bar max hold). The sweep re-runs
`add_signals(df, adx_thresh=X)` only — indicators and risk are
unchanged. The exit fade level stays at ADX < 20 throughout.

| ADX thr | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 25 | BTC | 13 | 15.4% | -$596 | -2.18 | 0.26 | -$45.83 |
| 25 | ETH | 11 | 18.2% | -$341 | -1.36 | 0.43 | -$31.01 |
| 25 | HYPE | 10 | 40.0% | +$590 | +1.48 | 2.08 | +$58.99 |
| 30 (shipped) | BTC | 3 | 0.0% | -$260 | -2.70 | 0.00 | -$86.75 |
| 30 (shipped) | ETH | 5 | 20.0% | -$164 | -0.97 | 0.46 | -$32.84 |
| 30 (shipped) | HYPE | 7 | 42.9% | +$287 | +0.94 | 1.77 | +$41.07 |
| 35 | BTC | 0 | — | $0 | 0.00 | — | $0.00 |
| 35 | ETH | 3 | 33.3% | -$12 | -0.07 | 0.92 | -$3.95 |
| 35 | HYPE | 3 | 33.3% | -$140 | -0.71 | 0.36 | -$46.60 |

## One-line verdict

- **25:** roughly doubles the trade count (34 combined) and the
  combined result gets worse (-$347, PF 0.26–0.43 on BTC/ETH). More
  trades, still no edge — loosening the filter just admits weaker
  trends.
- **30 (shipped):** 15 trades combined, -$137. The HYPE leg stays
  green (+$287, PF 1.77) but on 7 trades that is noise, not signal.
- **35:** 6 trades total across three coins — the setup is
  effectively dead at this threshold on 1h data.
- **Shipped decision:** keep the specified ADX threshold of 30 as
  the registry config regardless. It was fixed before any backtest
  was run; the sweep shows a monotone trade-off (lower threshold =
  more trades and worse results, higher = no trades) with no
  in-sample winner worth adopting. The honest read: the threshold
  is not the problem — ADX(14) > 30 + rising is simply a rare regime
  on 1h crypto, and the daily-chart setup needs a different clock
  or a different trend filter to trade the hourly.
