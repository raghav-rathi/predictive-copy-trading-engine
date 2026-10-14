# GMMA — Calibration Sweep

Shipped config: short EMA(3,5,8,10,12,15) / long EMA(30,35,40,45,50,60),
2xATR stop, 2.5xATR trail. Same data, costs, and sizing as BACKTEST.md.

## Variant table (combined across BTC+ETH+HYPE)

| Variant | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Profit factor |
|---|---|---|---|---|---|---|---|
| Shipped (base groups + trail) | 598 | 28.4% | -$5,790 | — | -1.71/-2.09/-0.78 | -28/-32/-17% | 0.74/0.72/0.86 |
| A: compressed groups (5,8,10,12,15,20 / 25,30,35,40,45,50) | 546 | 29.7% | -$4,455 | — | -1.49/-1.56/-0.33 | -25/-29/-16% | 0.75/0.77/0.93 |
| B: no trailing stop (2xATR stop only) | 598 | 22.4% | -$6,093 | — | -1.82/-1.64/+0.23 | -45/-38/-16% | 0.64/0.70/1.01 |

## One-line verdicts

- **Variant A (compressed groups):** improves loss by ~23% ($5.8k -> $4.5k)
  and HYPE nearly flattens (profit factor 0.93), but stays negative
  everywhere — compressing the groups reduces lag without fixing the
  whipsaw-entry problem. Slightly better, still a loser.
- **Variant B (no trail):** worse on BTC/ETH (drawdowns balloon to -45%),
  HYPE goes barely flat (+$96, profit factor 1.01) — the trail is
  net-positive for the system as a whole; HYPE's flip is one-coin noise,
  not an edge (181 trades, +1.4%).

## Takeaway

No variant flips the system positive; the failure is structural (entry
fires on routine 1h-bar noise, ~200+ trades/coin over 7 months), not
parametric. The sweep does not justify a re-ship — the calibration note
in BACKTEST.md stands: a real Guppy compression/count-back-line filter
before the crossover is the only rescue worth building next.
