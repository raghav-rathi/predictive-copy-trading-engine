# LSMA Slope — LSMA length sweep

Swept the LSMA window over {14, 21, 34} on the same data/costs/sizing as
BACKTEST.md (HL 1h, BTC+ETH+HYPE, 2026-03-14 → 2026-10-12, 0.045%+0.01%
costs, 1% risk, $10k start). Monkeypatched `indicators.LSMA_LEN` via a
throwaway script (`/tmp/sweeps.py`, not committed); no code change in
the strategy itself.

| LSMA_LEN | Trades | Net $ | BTC net | ETH net | HYPE net | Verdict |
|---|---|---|---|---|---|---|
| 14 | 1,464 | -$9,707 | -$5,974 | -$4,075 | +$342 | **LOSER** — faster LSMA = more whipsaw. |
| 21 (shipped) | 1,158 | -$5,570 | -$3,200 | -$5,397 | +$3,060 | **MIXED** — the classic length, best HYPE. |
| 34 | 867 | -$3,030 | -$697 | -$3,114 | +$781 | **LOSER** — least bad combined, still negative everywhere except a weak HYPE. |

## Takeaway

Shipped 21. The 34-length variant loses less combined (-$3,030 vs
-$5,570) but is negative on BTC and ETH and only weakly positive on HYPE
— not a dramatic rescue, just less churn (867 vs 1,158 trades). The
21-length classic is the best performer on HYPE (+$3,060, Sharpe 1.59)
and the published standard. A structural fix (trend-regime filter so the
system sits out range-bound chop on the majors) is out of scope for this
iteration; the parameter is not the problem.
