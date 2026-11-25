# KAMA Cross — Calibration

Fast-ER sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, pinned batch-46 window
2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC, 6,136 bars
BTC/ETH, 6,134 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 60-bar max hold). The fast ER period is the
strategy's natural knob: how quickly the fast KAMA's
efficiency ratio forgets the past — 5 adapts fastest, 20
makes the fast KAMA identical to the slow one. The sweep
re-runs `add_indicators(df, er_fast=X)` only — signals and
risk are unchanged.

| ER (fast) | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 5 | BTC | 256 | 31.6% | -$2,702 | -1.54 | 0.76 | -$10.55 |
| 5 | ETH | 237 | 34.6% | +$1,537 | +0.98 | 1.13 | +$6.49 |
| 5 | HYPE | 238 | 39.9% | +$866 | +0.65 | 1.07 | +$3.64 |
| 10 (shipped) | BTC | 232 | 31.0% | -$3,319 | -2.26 | 0.67 | -$14.30 |
| 10 (shipped) | ETH | 224 | 40.6% | +$228 | +0.35 | 1.02 | +$1.02 |
| 10 (shipped) | HYPE | 240 | 35.8% | +$1,788 | +1.00 | 1.13 | +$7.45 |
| 20 | BTC | 0 | — | $0 | 0.00 | — | $0.00 |
| 20 | ETH | 0 | — | $0 | 0.00 | — | $0.00 |
| 20 | HYPE | 0 | — | $0 | 0.00 | — | $0.00 |

## One-line verdict

- **5:** the least-bad combined read (-$298, 731 trades) —
  best on BTC (-$2,702 vs -$3,319 shipped) and ETH (+$1,537,
  Sharpe +0.98), worst on HYPE (+$866 vs +$1,788 shipped).
  Still negative combined.
- **10:** the shipped setting — combined -$1,302 on 696
  trades; the HYPE leg (+$1,788, Sharpe +1.00) is the best
  single-coin read in the sweep, the BTC leg (-$3,319,
  Sharpe -2.26) the worst.
- **20:** degenerate — zero trades on every coin. With the
  fast ER equal to the slow ER (20), the two KAMAs are the
  same series, so no cross can ever occur. A useful boundary
  check that the cross logic is really comparing two
  different averages, not a tunable setting.
- **Shipped decision:** keep the specified fast ER = 10 as
  the registry config regardless. It was fixed before any
  backtest was run; adopting 5 *because* it is less negative
  in-sample would be in-sample selection on a knob whose
  effect is not even consistent across coins (5 wins BTC and
  ETH, loses HYPE). The honest read: the ER knob moves the
  loss around between coins rather than removing it. Do not
  ship 5 on the strength of this sweep.

## Audit

- **Lookahead audit:** no lookahead found. The KAMA
  recursion reads only closes through the current bar (the
  ER window is the trailing n bars, with a partial window
  for i < n); signals use `crossed_above`/`crossed_below`
  on bars i and i−1 only; no `ichimoku` chikou column is
  used anywhere. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the recursion implemented is the
  textbook KAMA from the brief's source
  (https://docs.wickra.org/Indicators/Indicator-Kama):
  ER over 10 bars, SC = (ER × (2/3 − 2/31) + 2/31)²,
  seeded at the first close. The only judgement call is
  the partial ER window for i < n (documented in
  indicators.py); it affects only the first 10–20 bars,
  which are inside the 60-bar warmup anyway.
- **Tests:** 14/14 pass (`python3 -m unittest
  strategies.kama_cross.test_kama_cross`).
- **No parameter was tuned to PnL.** Fast ER stays 10.
