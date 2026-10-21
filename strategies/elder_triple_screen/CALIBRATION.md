# Elder Triple Screen — Calibration

MACD sensitivity on the 6h trend screen, same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-21, same costs/sizing,
2.5xATR stop, 3.5xATR trail, 150-bar max hold). The 6h MACD(12,26,9)
spans roughly 6.5 days of 1h bars; (8,17,9) reacts faster (~4.5 days),
(16,32,9) slower (~8.5 days). The sweep re-runs
`add_indicators(df, macd_fast=.., macd_slow=.., macd_signal=..)` only —
signals and risk are unchanged.

| MACD(6h) | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| (12,26,9) shipped | BTC | 186 | 24.2% | -$3,281 | -3.56 | 0.52 | -$17.64 |
| (12,26,9) shipped | ETH | 182 | 31.9% | -$1,662 | -1.43 | 0.73 | -$9.13 |
| (12,26,9) shipped | HYPE | 180 | 35.0% | -$1,759 | -1.84 | 0.73 | -$9.77 |
| (8,17,9) | BTC | 203 | 28.6% | -$3,208 | -3.55 | 0.56 | -$15.80 |
| (8,17,9) | ETH | 209 | 29.7% | -$2,933 | -2.96 | 0.58 | -$14.03 |
| (8,17,9) | HYPE | 186 | 38.2% | -$1,177 | -1.13 | 0.82 | -$6.33 |
| (16,32,9) | BTC | 177 | 23.2% | -$3,412 | -3.69 | 0.49 | -$19.27 |
| (16,32,9) | ETH | 178 | 27.0% | -$3,243 | -3.32 | 0.52 | -$18.22 |
| (16,32,9) | HYPE | 157 | 36.3% | -$1,262 | -1.27 | 0.78 | -$8.04 |

## One-line verdict

- **(12,26,9) shipped:** loses on all three (-$6,702 combined).
- **(8,17,9):** "least bad" everywhere (combined -$7,318 — actually
  worse combined than shipped, best only per-coin on BTC/HYPE) —
  still deeply negative on every coin.
- **(16,32,9):** worst of the three on BTC/ETH, combined -$7,917.
- **Shipped decision:** keep the specified MACD(12,26,9) as the
  registry config regardless. It was fixed before any backtest was
  run, and the sweep gives no reason to move: every cell loses, so
  there is no in-sample winner to be tempted by. The honest read is
  that the MACD speed is not the binding constraint — the whole
  tide-plus-wave construction is wrong for this window, and tuning
  the screen would be polishing a losing signal.
