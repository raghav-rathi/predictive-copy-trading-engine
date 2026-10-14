# Pivot Breakout — hard-stop sweep

Swept the hard-stop multiple over {1.5, 2.0, 2.5} x ATR(14) on the same
data/costs/sizing as BACKTEST.md (HL 1h, BTC+ETH+HYPE, 2026-03-14 →
2026-10-12, 0.045%+0.01% costs, 1% risk, $10k start). Monkeypatched
`risk.RISK.stop_atr_mult` via a throwaway script (`/tmp/sweeps.py`, not
committed); no code change in the strategy itself.

| Stop | Trades | Net $ | BTC net | ETH net | HYPE net | Verdict |
|---|---|---|---|---|---|---|
| 1.5x ATR | 356 | +$2,216 | +$1,155 | +$841 | +$220 | **WINNER (thin)** — best combined, +$347 over 2.0x. |
| 2.0x ATR (shipped) | 325 | +$1,869 | +$501 | +$844 | +$524 | **WINNER (thin)** — the classic published spec. |
| 2.5x ATR | 297 | +$2,158 | +$578 | +$1,183 | +$398 | **WINNER (thin)** — all three positive, wider stops. |

## Takeaway

Shipped 2.0x. All three stop values are positive on all three coins, so
2.0x sits in a stable region rather than on a knife edge — the edge
survives ±25% stop changes. The 1.5x variant is ~$350 better combined,
but that is not a dramatic improvement (under $1.10 per trade) and a
tighter stop on a breakout system is the classic way to get chopped in a
regime change. Kept the published 2.0x; the thin margin (PF ~1.06) is the
real story regardless of stop choice.
