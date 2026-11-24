# Three-Bar Reversal — Calibration

Confirmation-mode sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-11-24, window ms
`[1773525600000, 1795525200000)`, same costs/sizing, 2xATR stop,
3xATR trail, 60-bar max hold). Batch-45 re-run — the Nov-14 sweep
numbers this file previously carried are deleted, not preserved
alongside. Confirmation is the strategy's natural knob: how much
proof the turn needs before entry — `"high"` requires the
confirmation bar to close beyond the hook bar's high/low
(strictest), `"close"` only beyond its close, `"none"` enters on
the hook bar itself with no confirmation at all. The sweep
re-runs `add_signals(df, confirm=X)` only — indicators and risk
are unchanged.

| confirm | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| high (shipped) | BTC | 350 | 27.43% | -$5,737.97 | -4.70 | 0.55 | -$16.39 |
| high (shipped) | ETH | 275 | 32.36% | -$1,036.27 | -0.48 | 0.91 | -$3.77 |
| high (shipped) | HYPE | 357 | 37.25% | -$914.07 | -0.38 | 0.94 | -$2.56 |
| close | BTC | 479 | 28.81% | -$5,958.43 | -4.26 | 0.60 | -$12.44 |
| close | ETH | 408 | 31.62% | -$3,063.48 | -1.74 | 0.78 | -$7.51 |
| close | HYPE | 500 | 36.20% | -$2,199.49 | -1.07 | 0.88 | -$4.40 |
| none | BTC | 1,030 | 31.75% | -$7,506.99 | -5.88 | 0.58 | -$7.29 |
| none | ETH | 895 | 32.51% | -$5,884.53 | -3.94 | 0.70 | -$6.57 |
| none | HYPE | 1,106 | 36.71% | -$6,101.37 | -4.60 | 0.70 | -$5.52 |

Combined: high (shipped) -$7,688.32 on 982 trades; close
-$11,221.40 on 1,387 trades; none -$19,492.89 on 3,031 trades.

## One-line verdict

- **high (shipped):** least-bad combined (-$7,688.32 on 982 trades)
  — but that is an in-sample observation, not a justification.
  The strict confirmation filters out ~68% of the would-be
  entries and still loses.
- **close:** 1.4x the trades (1,387), combined -$11,221.40. Worse on
  every coin than "high"; the weaker confirmation admits entries
  that the strict bar would have rejected, and they lose.
- **none:** 3,031 trades, combined -$19,492.89, BTC -75.05%
  (Sharpe -5.88). Entering on the hook bar itself roughly triples
  the trade count and roughly doubles the loss — the hook alone,
  without a confirmation bar, is mostly noise.
- **Shipped decision:** keep the specified confirmation="high" as
  the registry config regardless. It was fixed before any backtest
  was run; adopting it *because* it is least-bad in-sample would
  still be in-sample selection. The honest read: the confirmation
  knob is monotonic — stricter is better — which says the pattern
  itself has no edge on 1h crypto and the best you can do is fire
  it less often.

## Batch-45 audit note

No bug was found and no parameter was changed in the batch-45
refresh: the audit found no lookahead, no NaN poisoning, and the
exit logic matches the spec. The only code change was filling in
the empty `source_url` in `__init__.py`
(https://www.luxalgo.com/library/concept/1-2-3-reversal/).
