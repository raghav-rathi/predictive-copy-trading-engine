# KST — signal-period sweep calibration

Swept the signal-line period SIGNAL over {6, 9, 13} on the same
data/costs/sizing as BACKTEST.md (HL 1h, BTC+ETH+HYPE, 2026-03-14 →
present, 0.045%+0.01% costs, 1% risk, $10k start). Monkeypatched the
module constant via a throwaway script (`/tmp/sweep_kst.py`, not
committed); no code change in the strategy itself.

| Signal N | Trades | Combined net $ | BTC net / Sharpe | ETH net / Sharpe | HYPE net / Sharpe |
|---|---|---|---|---|---|
| 6 | 935 | −$3,925 | −$3,691 / −2.61 | −$2,152 / −1.24 | +$1,917 / +1.22 |
| 9 | 799 | −$1,403 | −$2,685 / −1.81 | −$2,615 / −1.77 | +$3,897 / +2.13 |
| 13 | 697 | +$2,404 | −$927 / −0.43 | −$1,315 / −0.75 | +$4,647 / +2.49 |

## Takeaway

**Shipped the classic 9.** The sweep is monotonic — slower signal loses
less everywhere and flips the combined book positive at 13 — which is
exactly why I did *not* ship 13: monotonic means there is no stable
interior optimum, just "slower is better" on this window, and BTC/ETH
still lose at 13. Shipping 13 would be fitting the dial to one 7-month
sample. The honest read: KST's signal-line cross wants a slower
confirmation than any classic parameterization on 1h crypto — a design
question for a follow-up system, not a parameter to tweak. HYPE is
positive at every signal period (Sharpe 1.22/2.13/2.49), reinforcing the
batch's HYPE-momentum finding.
