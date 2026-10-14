# Dual Thrust — K sweep calibration

Swept the breakout multiplier K (K1=K2) over {0.5, 0.7, 0.9} on the same
data/costs/sizing as BACKTEST.md (HL 1h, BTC+ETH+HYPE, 2026-03-14 →
2026-10-10, 0.045%+0.01% costs, 1% risk, $10k start). Monkeypatched module
constants via a throwaway script (`/tmp/dt_k_sweep.py`, not committed);
no code change in the strategy itself.

| K | Trades | Net $ | BTC net | ETH net | HYPE net | Sharpe (BTC/ETH/HYPE) | Verdict |
|---|---|---|---|---|---|---|---|
| 0.5 | 130 | +$252 | -$666 | -$39 | +$958 | -0.93 / 0.03 / 1.13 | **LOSER** — tight lines fire into chop; win% collapses to 26–40% and fees eat the book. |
| 0.7 | 50 | +$2,813 | +$393 | +$1,034 | +$1,386 | 0.91 / 1.41 / 2.03 | **WINNER** — positive on all three, best combined net. |
| 0.9 | 25 | +$1,829 | +$177 | +$1,450 | +$202 | 0.58 / 2.10 / 0.56 | **WINNER, fragile** — positive everywhere but only 7–9 trades/coin; the Sharpe is noise-level at that count. |

## Takeaway

Shipped K=0.7. It is not on a knife edge: 0.9 is also positive but too
thin to trust (25 trades total), and 0.5 is a structural failure (lines
too tight → churn). The edge lives in letting the range be wide enough
that only genuine expansion days trigger. No per-coin K tuning — that
would be fitting to 14–19 trades.
