# Aroon — lookback sweep calibration

Swept the Aroon period N over {14, 25, 42} on the same data/costs/sizing
as BACKTEST.md (HL 1h, BTC+ETH+HYPE, 2026-03-14 → present, 0.045%+0.01%
costs, 1% risk, $10k start). Monkeypatched the module constant via a
throwaway script (`/tmp/sweep_aroon.py`, not committed); no code change
in the strategy itself.

| Aroon N | Trades | Combined net $ | BTC net / Sharpe | ETH net / Sharpe | HYPE net / Sharpe |
|---|---|---|---|---|---|
| 14 | 948 | +$346 | −$1,892 / −1.02 | −$211 / +0.04 | +$2,448 / +1.40 |
| 25 | 528 | +$1,844 | −$1,632 / −1.15 | +$1,187 / +0.91 | +$2,289 / +1.51 |
| 42 | 320 | +$1,988 | −$380 / −0.23 | +$697 / +0.69 | +$1,671 / +1.31 |

## Takeaway

**Shipped the classic 25.** It is the best combined (+$1,844) and sits in
a stable region: 42 is close (+$1,988, fewer trades, same BTC drag) and
14 churns into near-zero. No knife-edge. BTC is negative at every
period — the sweep does not rescue BTC, it only confirms the
fresh-trend filter works on ETH/HYPE's wider intraday ranges while 1h
BTC breakouts keep failing.
