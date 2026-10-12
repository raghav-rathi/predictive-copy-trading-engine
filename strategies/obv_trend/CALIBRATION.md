# OBV Trend — trend-filter EMA sweep

Swept the price trend filter EMA length over {34, 50, 100} on the same
data/costs/sizing as BACKTEST.md (HL 1h, BTC+ETH+HYPE, 2026-03-14 →
2026-10-12, 0.045%+0.01% costs, 1% risk, $10k start). Monkeypatched
`indicators.TREND_EMA` via a throwaway script (`/tmp/sweeps.py`, not
committed); no code change in the strategy itself.

| TREND_EMA | Trades | Net $ | BTC net | ETH net | HYPE net | Verdict |
|---|---|---|---|---|---|---|
| 34 | 1,571 | -$10,006 | -$6,096 | -$4,266 | +$356 | **LOSER** — faster filter just fires more. |
| 50 (shipped) | 1,445 | -$10,267 | -$5,700 | -$3,833 | -$734 | **LOSER** — the classic construction. |
| 100 | 1,253 | -$7,948 | -$4,912 | -$2,511 | -$525 | **LOSER** — less churn, still a uniform bleed. |

## Takeaway

Shipped 50. Longer filters reduce the trade count (1,571 → 1,253) but
lose money at every length; the EMA(100) variant is not dramatically
better — it is negative on all three coins with the same ~20% win rate.
The problem is the dual-alignment trigger firing into chop, not the
window length. A structural fix (daily regime filter, or OBV divergence
entries instead of alignment entries) is out of scope for this iteration.
