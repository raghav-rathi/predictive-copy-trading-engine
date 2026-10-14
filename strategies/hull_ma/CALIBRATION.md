# Hull MA — period sweep calibration

Swept the HMA period N over {8, 16, 32} on the same data/costs/sizing as
BACKTEST.md (HL 1h, BTC+ETH+HYPE, 2026-03-14 → present, 0.045%+0.01%
costs, 1% risk, $10k start). Monkeypatched the module constant via a
throwaway script (`/tmp/sweep_hma.py`, not committed); no code change in
the strategy itself.

| HMA N | Trades | Combined net $ | BTC net / Sharpe | ETH net / Sharpe | HYPE net / Sharpe |
|---|---|---|---|---|---|
| 8 | 3,121 | −$21,915 | −$7,945 / −9.82 | −$6,929 / −7.26 | −$7,041 / −9.13 |
| 16 | 1,916 | −$15,834 | −$6,896 / −7.39 | −$5,093 / −3.98 | −$3,846 / −3.02 |
| 32 | 1,084 | −$7,022 | −$5,090 / −4.69 | −$3,368 / −2.51 | +$1,435 / +1.09 |

## Takeaway

**Shipped the classic 16.** The sweep is monotonic — slower HMA loses
less — but no period is positive combined: N=32 still loses −$7,022 with
BTC/ETH deeply negative, and HYPE's +$1,435 at Sharpe 1.09 is one coin
out of nine cells. There is no stable winning region to switch to; the
mechanism (raw slope-sign flips on 1h bars) is the problem, not the
period. The sweep direction does say where a fix would live: a slower
HMA plus a slope-magnitude confirmation filter, i.e. a different system.
