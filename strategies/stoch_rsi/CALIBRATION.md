# StochRSI — OS/OB threshold sweep

Swept the entry-zone thresholds (OS, OB) over {(15,85), (20,80), (25,75)}
on the same data/costs/sizing as BACKTEST.md (HL 1h, BTC+ETH+HYPE,
2026-03-14 → 2026-10-12, 0.045%+0.01% costs, 1% risk, $10k start).
Monkeypatched `signals.OS`/`signals.OB` via a throwaway script
(`/tmp/sweeps.py`, not committed); no code change in the strategy itself.

| OS/OB | Trades | Net $ | BTC net | ETH net | HYPE net | Verdict |
|---|---|---|---|---|---|---|
| 15/85 | 1,077 | -$12,892 | -$4,908 | -$3,544 | -$4,440 | **LOSER** — fewer trades, same uniform bleed. |
| 20/80 (shipped) | 1,339 | -$14,159 | -$5,295 | -$4,010 | -$4,855 | **LOSER** — the classic published parameters. |
| 25/75 | 1,560 | -$15,325 | -$5,330 | -$4,939 | -$5,056 | **LOSER** — wider zones just mean more churn. |

## Takeaway

Shipped 20/80. The sweep is flat-negative across the board: no threshold
choice is even positive on one coin, let alone all three. The system is
structurally broken on 1h crypto (whipsaw cross entries + immediate
opposite-cross exits), not mis-tuned. A fix would require changing the
mechanism itself (e.g. daily timeframe, or confirmation filters), which
is out of scope for this iteration.
