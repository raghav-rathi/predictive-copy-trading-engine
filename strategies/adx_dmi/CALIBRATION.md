# ADX/DMI — ADX threshold sweep calibration

Swept the entry filter ADX_ENTRY over {20, 25, 30} on the same
data/costs/sizing as BACKTEST.md (HL 1h, BTC+ETH+HYPE, 2026-03-14 →
present, 0.045%+0.01% costs, 1% risk, $10k start). Monkeypatched the
module constant via a throwaway script (`/tmp/sweep_adx.py`, not
committed); no code change in the strategy itself.

| ADX entry | Trades | Combined net $ | BTC net / Sharpe | ETH net / Sharpe | HYPE net / Sharpe |
|---|---|---|---|---|---|
| 20 | 497 | −$6,194 | −$2,986 / −2.90 | −$2,286 / −2.77 | −$922 / −0.68 |
| 25 | 234 | −$2,694 | −$519 / −0.50 | −$997 / −1.49 | −$1,178 / −1.87 |
| 30 | 116 | −$1,328 | −$648 / −1.28 | −$884 / −1.70 | +$204 / +0.46 |

## Takeaway

**Shipped the classic 25.** All three thresholds lose combined; 30 is
only "least bad" (halved trade count, HYPE barely positive at Sharpe
0.46) — that is not a stable winning region, it is the same losing
mechanism with less churn. The failure is structural: on 1h crypto the
DI cross forms after the move. No threshold rescue, so no reason to
deviate from the published 25.
