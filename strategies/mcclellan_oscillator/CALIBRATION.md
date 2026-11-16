# McClellan Oscillator — Calibration

EMA-length sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-11-16, same costs/sizing, 1.5xATR
stop, 2.5xATR target, 48-bar max hold). The sweep re-runs
`add_indicators(df, fast=X, slow=Y)` only — signals and risk are
unchanged.

| EMA fast/slow | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10/21 | BTC | 102 | 24.5% | -$3,314 | -3.12 | 0.49 | -$32.49 |
| 10/21 | ETH | 93 | 38.7% | -$591 | -0.52 | 0.90 | -$6.36 |
| 10/21 | HYPE | 117 | 40.2% | +$205 | +0.27 | 1.03 | +$1.75 |
| 19/39 (shipped) | BTC | 56 | 32.1% | -$1,038 | -1.25 | 0.71 | -$18.53 |
| 19/39 (shipped) | ETH | 63 | 30.2% | -$1,492 | -1.86 | 0.64 | -$23.68 |
| 19/39 (shipped) | HYPE | 71 | 32.4% | -$1,451 | -1.80 | 0.70 | -$20.44 |
| 30/50 | BTC | 6 | 16.7% | -$301 | -1.14 | 0.32 | -$50.18 |
| 30/50 | ETH | 7 | 57.1% | +$342 | +1.35 | 2.22 | +$48.90 |
| 30/50 | HYPE | 11 | 36.4% | -$120 | -0.29 | 0.84 | -$10.89 |

## One-line verdict

- **10/21:** the chop setting — 93–117 trades per coin, combined
  -$3,700. Faster EMAs cross more often and lose hardest on BTC
  (-$3,314, Sharpe -3.12, PF 0.49); only HYPE stays green (+$205).
- **30/50:** nearly breakeven combined (-$79) but on 24 trades
  total — 6–11 per coin. ETH's +$342 on 7 trades (win rate 57.1%,
  PF 2.22) is a 7-trade anecdote, not a setting.
- **19/39 (shipped):** worst combined (-$3,980) but the only
  setting with a usable trade count on every coin (56–71) — and
  that is an in-sample observation, not a justification; all three
  settings lose on at least two of three coins.
- **Shipped decision:** keep the specified 19/39 as the registry
  config regardless. The 19/39 lengths were fixed before any
  backtest was run; the in-sample ranking does not change that, and
  leaning toward 30/50 *because* its 24-trade total happens to sum
  near zero would be in-sample selection on noise. The honest read:
  the EMA length moves which coin pays and how often, not whether
  the breadth proxy works — on this window it does not, at any
  length.
