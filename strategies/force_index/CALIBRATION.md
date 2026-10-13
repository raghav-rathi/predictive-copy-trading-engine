# Elder Force Index pullback — Calibration

Shipped the classic Elder parameters: FI13 (trend) / FI2 (trigger),
2.5xATR(14) stop.

## Sweep: trend_n ∈ {8, 13, 21} × trigger_n ∈ {2, 3}

Same data, costs, and risk as BACKTEST.md. Combined net PnL over BTC+ETH+HYPE:

| trend_n | trig_n | BTC net $ | ETH net $ | HYPE net $ | Combined net $ | Trades |
|---|---|---|---|---|---|---|
| 8 | 2 | -5,858 | -5,119 | -797 | -11,774 | 2,363 |
| 8 | 3 | -4,380 | -3,922 | -347 | **-8,649** | 1,663 |
| 13 | 2 | -5,871 | -4,552 | -1,478 | -11,901 | 2,533 |
| 13 | 3 | -4,443 | -3,669 | -1,061 | -9,173 | 1,893 |
| 21 | 2 | -6,486 | -4,945 | -1,940 | -13,370 | 2,598 |
| 21 | 3 | -5,411 | -4,153 | -1,515 | -11,078 | 1,990 |

## Verdict: ship the classic 13/2

Every parameter combination is negative on all three coins — there is no
stable alternative to switch to. A slower trigger (trig_n=3) loses less
everywhere (fewer, cleaner crosses), and the 8/3 combo is the least-bad,
but "least bad" is still −$8.6k combined with Sharpe −0.4 to −6.9. No
re-tuning on a losing structure; shipped Elder's published 13/2 exactly as
documented, losses reported as losses.
