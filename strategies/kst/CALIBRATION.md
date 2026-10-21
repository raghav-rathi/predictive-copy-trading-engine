# Know Sure Thing — Calibration

Signal-line length sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-21 13:00 UTC, same
costs/sizing, 2xATR stop, 3xATR trail, 200-bar max hold). The sweep
re-runs `add_indicators(df, signal_n=X)` only — signals and risk are
unchanged.

| Signal | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 6 | BTC | 239 | 31.4% | -$3,411 | -2.82 | 0.67 | -$14.27 |
| 9 (shipped) | BTC | 202 | 32.7% | -$2,287 | -1.72 | 0.76 | -$11.32 |
| 14 | BTC | 174 | 35.6% | -$1,084 | -0.66 | 0.88 | -$6.23 |
| 6 | ETH | 231 | 33.8% | -$1,687 | -1.15 | 0.84 | -$7.30 |
| 9 (shipped) | ETH | 206 | 34.0% | -$1,846 | -1.34 | 0.82 | -$8.96 |
| 14 | ETH | 181 | 38.1% | -$935 | -0.64 | 0.90 | -$5.17 |
| 6 | HYPE | 223 | 37.7% | +$3,688 | +2.09 | 1.29 | +$16.54 |
| 9 (shipped) | HYPE | 198 | 41.4% | +$5,582 | +2.89 | 1.45 | +$28.19 |
| 14 | HYPE | 172 | 43.0% | +$5,393 | +2.92 | 1.52 | +$31.35 |

## One-line verdict

- **6:** twitchiest signal, most trades, worst everywhere
  (BTC -$3,411, Sharpe -2.82; HYPE leg weakest at +$3,688).
  Shortening the trigger adds whipsaw on every coin.
- **9 (shipped):** best HYPE leg (+$5,582, PF 1.45, expectancy
  +$28.19) but worst on ETH (-$1,846); combined +$1,449.
- **14:** smoothest cross, fewest trades; best on BTC (-$1,084)
  and ETH (-$935) — still red — and nearly matches 9 on HYPE
  (+$5,393, PF 1.52, expectancy +$31.35). In-sample combined
  winner at +$3,374.
- **Shipped decision:** keep the standard signal=9 as the registry
  config regardless. The 9 was fixed before any backtest was run
  (Pring's canonical length); the sweep shows 14 is smoother and
  less bad on the losers, but adopting it because it wins this
  7-month in-sample would still be in-sample selection. The right
  choice needs walk-forward or out-of-sample evidence.
