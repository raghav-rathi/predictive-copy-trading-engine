# Money Flow Index — OS/OB threshold sweep

Swept the reversal thresholds (OS, OB) over {(10,90), (20,80), (30,70)}
on the same data/costs/sizing as BACKTEST.md (HL 1h, BTC+ETH+HYPE,
2026-03-14 → 2026-10-12, 0.045%+0.01% costs, 1% risk, $10k start).
Monkeypatched `signals.OS`/`signals.OB` via a throwaway script
(`/tmp/sweeps.py`, not committed); no code change in the strategy itself.

| OS/OB | Trades | Net $ | BTC net | ETH net | HYPE net | Verdict |
|---|---|---|---|---|---|---|
| 10/90 | 88 | -$3,615 | -$1,261 | -$1,258 | -$1,096 | **LOSER** — least bad, still negative everywhere on 88 trades. |
| 20/80 (shipped) | 377 | -$5,770 | +$298 | -$3,816 | -$2,252 | **LOSER** — BTC breakeven, majors lose. |
| 30/70 | 739 | -$5,530 | -$1,370 | -$3,156 | -$1,005 | **LOSER** — looser zones double the churn. |

## Takeaway

Shipped 20/80. The 10/90 variant loses less in absolute dollars but is
still negative on all three coins — it is not "dramatically better" in
any meaningful sense (no positive coin, no stable edge), and at 88 trades
its advantage is noise. The failure is structural: fading volume-backed
momentum on 1h crypto. Kept the published 20/80 so the reported result
matches the canonical indicator definition.
