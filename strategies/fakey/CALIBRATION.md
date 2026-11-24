# Fakey — Calibration

False-break confirmation sensitivity on the same Hyperliquid 1h
data as BACKTEST.md (BTC/ETH/HYPE, window ms
`[1773525600000, 1795525200000)`, 2026-03-14 22:00 UTC →
2026-11-24 14:00 UTC, same costs/sizing, 2xATR stop, 3xATR
trail, 60-bar max hold). Re-run on the batch-45 window; the
stale Nov-14 sweep numbers have been replaced. The confirmation
is the strategy's natural knob: "mother" (shipped) accepts any
close back inside the mother bar's range, "inside" demands the
break bar fully reclaim the inside bar's range (close[i] >
low[i-1] for bullish / close[i] < high[i-1] for bearish) — a
stricter confirmation that filters out shallow reclaims. The
sweep re-runs `add_signals(df, confirm=X)` only — indicators
and risk are unchanged.

| confirm | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| mother (shipped) | BTC | 383 | 40.47% | -$3,968.86 | -2.60 | 0.68 | -$10.36 |
| mother (shipped) | ETH | 421 | 40.14% | -$2,897.39 | -1.59 | 0.82 | -$6.88 |
| mother (shipped) | HYPE | 331 | 38.67% | -$2,567.75 | -1.65 | 0.83 | -$7.76 |
| inside | BTC | 297 | 36.36% | -$2,865.25 | -1.87 | 0.76 | -$9.65 |
| inside | ETH | 315 | 37.14% | -$939.66 | -0.38 | 0.93 | -$2.98 |
| inside | HYPE | 261 | 34.10% | -$3,298.59 | -2.47 | 0.71 | -$12.64 |

Combined: mother 1,135 trades, -$9,434.01; inside 873 trades,
-$7,103.50.

## One-line verdict

- **mother (shipped):** loosest confirmation, most trades
  (1,135) — worst combined (-$9,434.01), worst on BTC
  (-$3,968.86) and ETH (-$2,897.39). More setups, same negative
  edge, more fees.
- **inside:** stricter confirmation, fewer trades (873) —
  less bad combined (-$7,103.50) and dramatically less bad on
  ETH (-$939.66, PF 0.93, Sharpe -0.38 — the closest thing to
  breakeven in this strategy), but worse on HYPE (-$3,298.59,
  expectancy -$12.64, the worst per-trade loss in the sweep).
  Stricter confirmation helps where the reclaim is genuinely
  strong and hurts where it filters out the trades that would
  have worked — no consistent direction.
- **Shipped decision:** keep the specified mother-bar
  confirmation as the registry config regardless. It was fixed
  before any backtest was run; adopting "inside" *because* it
  is less bad in-sample would still be in-sample selection. The
  honest read: the knob moves the combined net by only ~$2,300
  across settings and every setting is negative on every coin,
  which says the problem is not how the close-back is defined —
  it is that a 3-bar false-break pattern on 1h crypto does not
  predict the reversal in the first place.

## Batch-45 audit note

Refresh audit (Nov 24, 2026): no lookahead, no NaN poisoning,
no exit-logic bug found in indicators/signals/risk. All 14
tests pass. No code changed; parameters untouched. The only
file change in this refresh was filling in the empty
`source_url` in `__init__.py` (verified Nial Fuller article:
https://www.learntotradethemarket.com/forex-trading-strategies/what-is-fakey-pattern).
