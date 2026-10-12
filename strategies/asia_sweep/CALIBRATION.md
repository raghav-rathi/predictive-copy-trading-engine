# Asia Sweep — sweep-depth calibration

Swept the minimum sweep-depth multiplier (sweep must extend
DEPTH_ATR_MULT × ATR(14) past the session extreme) over {0.05, 0.10,
0.15} on the same data/costs/sizing as BACKTEST.md (HL 1h, BTC+ETH+HYPE,
2026-03-14 → 2026-10-10, 0.045%+0.01% costs, funding accrued, 1% risk,
$10k start). Monkeypatched module constant via a throwaway script
(`/tmp/as_sweep.py`, not committed); no strategy code changed.

| Depth | Total trades | Total net $ | BTC | ETH | HYPE |
|---|---|---|---|---|---|
| 0.05 | 141 | **−$3,963** | 47t / −$1,422, WR 30%, PF 0.62 | 49t / −$887, WR 31%, PF 0.77 | 45t / −$1,654, WR 27%, PF 0.53 |
| 0.10 (spec) | 126 | **−$3,488** | 45t / −$1,211, WR 31%, PF 0.66 | 41t / −$964, WR 29%, PF 0.71 | 40t / −$1,314, WR 28%, PF 0.58 |
| 0.15 | 109 | **−$3,519** | 38t / −$1,391, WR 26%, PF 0.57 | 36t / −$1,125, WR 28%, PF 0.63 | 35t / −$1,003, WR 29%, PF 0.64 |

## Takeaway

Shipped the spec's 0.10x. The sweep is uniformly negative — every depth
loses on every coin with profit factors 0.53–0.77 — so the failure is
structural, not a depth-tuning problem. Looser depth (0.05x) just adds
more losing trades; tighter depth (0.15x) doesn't filter the losers out.
No per-coin depth tuning: there is nothing here to tune toward.
