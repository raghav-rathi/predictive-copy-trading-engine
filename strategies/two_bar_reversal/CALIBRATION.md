# Two-Bar Key Reversal — Calibration

Confirmation-mode sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-11-24, window ms
`[1773525600000, 1795525200000)`, same costs/sizing, 2xATR stop,
3xATR trail, 60-bar max hold). Batch-45 re-run — the Nov-14 sweep
numbers this file previously carried are deleted, not preserved
alongside. Confirmation is the strategy's natural knob: how much
proof the turn needs before entry — `"high"` requires the
confirmation bar to close beyond the pattern bar's high/low
(strictest), `"close"` only beyond its close, `"none"` enters on
the pattern bar itself with no confirmation at all. The sweep
re-runs `add_signals(df, confirm=X)` only — indicators and risk
are unchanged.

| confirm | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| high (shipped) | BTC | 387 | 31.01% | -$5,281.93 | -4.01 | 0.59 | -$13.65 |
| high (shipped) | ETH | 386 | 31.61% | -$2,311.94 | -1.11 | 0.84 | -$5.99 |
| high (shipped) | HYPE | 402 | 35.07% | +$212.05 | 0.25 | 1.01 | +$0.53 |
| close | BTC | 1,661 | 33.11% | -$9,253.10 | -11.08 | 0.49 | -$5.57 |
| close | ETH | 1,669 | 34.27% | -$7,906.74 | -6.05 | 0.66 | -$4.74 |
| close | HYPE | 1,723 | 36.51% | -$8,144.66 | -7.33 | 0.62 | -$4.73 |
| none | BTC | 2,205 | 48.34% | -$9,755.57 | -13.61 | 0.46 | -$4.42 |
| none | ETH | 2,262 | 50.93% | -$9,646.97 | -11.77 | 0.48 | -$4.26 |
| none | HYPE | 2,161 | 53.77% | -$9,131.40 | -9.72 | 0.66 | -$4.23 |

Combined: high (shipped) -$7,381.81 on 1,175 trades; close
-$25,304.50 on 5,053 trades; none -$28,533.94 on 6,628 trades.

## One-line verdict

- **high (shipped):** least-bad combined (-$7,381.81 on 1,175
  trades) — but that is an in-sample observation, not a
  justification. The strict confirmation filters out ~75% of the
  would-be entries and still loses.
- **close:** 4.3x the trades (5,053), combined -$25,304.50. Win rate
  ticks up a point or two, expectancy per trade improves slightly,
  but the extra trades are all fee-paying losers in aggregate —
  weaker confirmation admits noise faster than edge.
- **none:** 6,628 trades, combined -$28,533.94, BTC/ETH books
  effectively wiped out (-97.56% / -96.47%, Sharpe -13.61 /
  -11.77). Tellingly the win rate *rises* to 48–54% — entering on
  the pattern bar catches the bounce more often — but profit
  factor collapses to 0.46–0.66: the wins are small and the
  losers (2xATR stops into resuming trends) are much bigger.
  Win rate without expectancy is a trap.
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
(http://www.solerinvestments.com/Online-Trading/Larry-Williams-Trading.htm).
