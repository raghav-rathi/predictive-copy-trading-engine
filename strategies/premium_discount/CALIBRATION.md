# Premium/Discount — Calibration

Range-lookback sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-11-24, batch-45
frozen window `[1773525600000, 1795525200000)`, same
costs/sizing, 2xATR stop, 3xATR trail, 60-bar max hold). The
lookback is the strategy's natural knob: how wide the dealing
range is — 24 is a short, twitchy range (more setups), 96 a
long, slow one (fewer setups). The sweep re-runs
`add_indicators(df, lookback=X)` only — signals and risk are
unchanged. Re-run for batch 45; the Nov-14 sweep is superseded.

| lookback | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy | Fees $ |
|---|---|---|---|---|---|---|---|---|
| 24 | BTC | 521 | 24.38% | -$4,188.83 | -2.37 | 0.75 | -$8.04 | $4,380.40 |
| 24 | ETH | 530 | 21.51% | -$4,438.17 | -2.55 | 0.74 | -$8.37 | $3,716.75 |
| 24 | HYPE | 502 | 23.51% | +$658.74 | +0.52 | 1.04 | +$1.31 | $2,635.84 |
| 48 (shipped) | BTC | 292 | 22.60% | -$2,965.86 | -2.08 | 0.72 | -$10.16 | $2,638.34 |
| 48 (shipped) | ETH | 256 | 25.78% | -$574.31 | -0.21 | 0.94 | -$2.24 | $2,079.32 |
| 48 (shipped) | HYPE | 268 | 23.88% | +$1,552.77 | +1.04 | 1.14 | +$5.79 | $1,501.54 |
| 96 | BTC | 126 | 23.81% | -$567.39 | -0.48 | 0.88 | -$4.50 | $1,182.76 |
| 96 | ETH | 127 | 19.69% | -$1,322.19 | -1.26 | 0.71 | -$10.41 | $922.66 |
| 96 | HYPE | 124 | 18.55% | +$142.32 | +0.22 | 1.03 | +$1.15 | $580.04 |

Combined totals: 24 → 1,553 trades, -$7,968.26 net, $10,732.99
fees; 48 (shipped) → 816 trades, -$1,987.40 net, $6,219.21
fees; 96 → 377 trades, -$1,747.26 net, $2,685.46 fees.

## One-line verdict

- **24:** loosest range, most trades (1,553) — worst combined
  (-$7,968.26) and worst on BTC and ETH (both ≈ -$4,300). More
  crosses, same failed reclaims, far more fees ($10,732.99).
- **96:** strictest range, fewest trades (377) — least-bad
  combined (-$1,747.26) and best on BTC (-$567.39) but still
  negative on BTC and ETH; HYPE barely positive (+$142.32).
  Fewer trades just means fewer chances to lose.
- **48:** middle ground (-$1,987.40 combined) and best on ETH
  and HYPE — but that is an in-sample observation, not a
  justification. Note 96 now edges 48 combined (-$1,747.26 vs
  -$1,987.40), a $240 gap on 377 vs 816 trades — noise, not a
  reason to switch.
- **Shipped decision:** keep the specified lookback=48 as the
  registry config regardless. It was fixed before any backtest
  was run; adopting it *because* it is least-bad in-sample
  would still be in-sample selection. The honest read: the
  knob moves the loss around (combined net spans -$1,747.26 to
  -$7,968.26, all negative) but never flips it — the problem is
  not how wide the range is, it is that an equilibrium cross
  after a range sweep does not predict continuation on 1h
  crypto in the first place.

## Batch-45 audit (no code changes)

Lookahead audit of indicators.py / signals.py / risk.py against
`strategies/base.py`: all rolling windows use `min_periods=n`
and include bar j only; `touched_discount`/`touched_premium`
compare the 12-bar trailing low/high against the current bar's
own discount/premium level; crosses use `crossed_above`/
`crossed_below`, which compare bar j against `shift(1)` — no
future data anywhere. The truncation test
(`test_no_lookahead_truncation`) passes. No bug was found, so
no code was changed and no parameter was tuned. The only edit
in batch 45 was filling in the empty `source_url` in
`__init__.py` with
https://www.luxalgo.com/library/concept/premium-and-discount/
(LuxAlgo's premium/discount reference, attributing the
convention to Michael J. Huddleston / ICT, verified via web
search 2026-11-24).
