# TRIX — period sweep calibration

Swept the TRIX period N over {10, 15, 21} on the same data/costs/sizing
as BACKTEST.md (HL 1h, BTC+ETH+HYPE, 2026-03-14 → present, 0.045%+0.01%
costs, 1% risk, $10k start). Monkeypatched the module constant via a
throwaway script (`/tmp/sweep_trix.py`, not committed); no code change in
the strategy itself.

| TRIX N | Trades | Combined net $ | BTC net / Sharpe | ETH net / Sharpe | HYPE net / Sharpe |
|---|---|---|---|---|---|
| 10 | 728 | −$1,594 | −$3,592 / −2.80 | −$2,016 / −1.36 | +$4,013 / +2.34 |
| 15 | 526 | +$5,118 | −$265 / +0.02 | +$55 / +0.16 | +$5,328 / +2.95 |
| 21 | 424 | +$3,310 | +$702 / +0.74 | +$181 / +0.25 | +$2,427 / +1.74 |

## Takeaway

**Shipped the classic 15.** It is the best combined (+$5,118) and not on
a knife edge — 21 is also positive (+$3,310) while 10 churns into a loss
(faster triple-EMA = more whipsaw). HYPE is positive at every period
(Sharpe 2.34/2.95/1.74), which strengthens the read that the HYPE edge is
real, not a fitted artifact of N=15. BTC/ETH hover near zero at 15 and
21 — the system is harmless there, not destructive.
