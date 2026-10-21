# Vortex Indicator Crossover — Calibration

Window sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-10-21, same costs/sizing, 2xATR stop,
3xATR trail, 120-bar max hold). The sweep re-runs
`add_indicators(df, n=X)` only — signals and risk are unchanged. The
sweep ran with END=1792589130654 (same 1h candle set as the main run).

| Window | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10 | BTC | 726 | 26.6% | -$7,052 | -5.98 | 0.58 | -$9.71 |
| 10 | ETH | 725 | 30.8% | -$4,463 | -2.77 | 0.77 | -$6.16 |
| 10 | HYPE | 620 | 33.9% | -$425 | -0.04 | 0.98 | -$0.69 |
| 14 (shipped) | BTC | 557 | 28.5% | -$5,326 | -3.85 | 0.66 | -$9.56 |
| 14 (shipped) | ETH | 596 | 31.4% | -$2,511 | -1.29 | 0.87 | -$4.21 |
| 14 (shipped) | HYPE | 523 | 32.1% | -$738 | -0.24 | 0.96 | -$1.41 |
| 20 | BTC | 485 | 27.2% | -$4,903 | -3.69 | 0.64 | -$10.11 |
| 20 | ETH | 468 | 29.9% | -$2,367 | -1.38 | 0.85 | -$5.06 |
| 20 | HYPE | 405 | 36.5% | +$3,664 | +1.87 | 1.23 | +$9.05 |

## One-line verdict

- **n=10:** worst on every coin (726 BTC trades — pure chop-churn;
  combined -$11,940). Shorter windows just add more flicker.
- **n=20:** best combined (-$3,606) and the only positive HYPE read
  (+$3,664, Sharpe +1.87, PF 1.23) — longer windows calm the cross
  enough for HYPE's trend legs to pay — but BTC (-$4,903) and ETH
  (-$2,367) stay deeply negative, so no window rescues the strategy.
- **n=14:** middling everywhere, combined -$8,576 — the worst of
  neither world, the best of none.
- **Shipped decision:** keep the specified n=14 as the registry
  config regardless. The n=14 window was fixed before any backtest was
  run; the in-sample ranking (n=20 best combined) does not change
  that, and even the best window is a combined loser. The honest read:
  the window is a tuning knob on a strategy that is structurally
  unsuited to 1h bars — the fix is a trend filter or entry
  confirmation, not a longer window. Any change needs walk-forward or
  out-of-sample evidence, not this 7-month window.
