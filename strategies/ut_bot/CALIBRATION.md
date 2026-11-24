# UT Bot Alerts — Calibration

KeyValue sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, pinned batch-45 window
2026-03-14 22:00 UTC → 2026-11-24 14:00 UTC, 6,111 bars
BTC/ETH, 6,109 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 60-bar max hold). KeyValue is the strategy's natural
knob: how far the trailing stop sits from price, in units of
ATR(10) — 1.0 hugs price (many flips), 3.0 gives it room
(few flips). The sweep re-runs `add_indicators(df,
key_value=X)` only — signals and risk are unchanged.
Sweep re-run for the batch-45 refresh; the Nov-14 sweep
numbers are deleted, not carried over.

| KeyValue | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 1.0 (shipped) | BTC | 677 | 30.6% | -$6,338 | -4.11 | 0.68 | -$9.36 |
| 1.0 (shipped) | ETH | 627 | 32.4% | -$3,285 | -1.44 | 0.84 | -$5.24 |
| 1.0 (shipped) | HYPE | 704 | 35.7% | -$2,701 | -1.23 | 0.89 | -$3.84 |
| 2.0 | BTC | 276 | 34.1% | -$1,519 | -0.60 | 0.89 | -$5.50 |
| 2.0 | ETH | 252 | 36.5% | +$1,487 | +0.88 | 1.12 | +$5.90 |
| 2.0 | HYPE | 282 | 35.5% | +$1,173 | +0.73 | 1.07 | +$4.16 |
| 3.0 | BTC | 166 | 31.9% | -$2,698 | -1.91 | 0.68 | -$16.26 |
| 3.0 | ETH | 156 | 33.3% | -$687 | -0.30 | 0.92 | -$4.40 |
| 3.0 | HYPE | 160 | 36.9% | +$3,494 | +1.93 | 1.35 | +$21.83 |

## One-line verdict

- **1.0:** the shipped setting — catastrophic combined
  (-$12,325, 2,008 trades, $11,640 in fees). The stop flips
  on noise and every flip charges admission.
- **2.0:** the only clearly positive combined read (+$1,141,
  810 trades) — positive on ETH (+$1,487, PF 1.12) and HYPE
  (+$1,173, PF 1.07), still negative on BTC (-$1,519).
  Fewer flips, less chop, less fees ($6,477).
- **3.0:** near-breakeven combined (+$108, 482 trades) —
  worst on BTC (-$2,698, expectancy -$16.26/trade) but the
  best single-coin read in the whole batch on HYPE (+$3,494,
  Sharpe +1.93, PF 1.35). The knob is unstable: 2.0 wins
  combined, 3.0 wins HYPE by a mile and loses BTC badly.
- **Shipped decision:** keep the specified KeyValue=1.0 as
  the registry config regardless. It was fixed before any
  backtest was run; adopting 2.0 *because* it is positive
  in-sample would be in-sample selection on a knob whose
  effect is not even monotone (1.0 → -$12,325, 2.0 →
  +$1,141, 3.0 → +$108). The honest read: the shipped
  1.0×ATR stop is structurally too tight for 1h crypto,
  and the sweep shows the "right" width is not
  identifiable from this window — 2.0 and 3.0 disagree
  violently by coin. Do not ship 2.0 on the strength of
  this sweep.

## Batch-45 refresh audit (2026-11-24)

- **Lookahead audit:** no lookahead found. The ATR is
  Wilder's causal ewm; the stop recursion reads only the
  previous bar's stop and close (plus the current bar's
  close and nLoss); signals use `crossed_above`/`crossed_below`
  on bars i and i−1 only. The truncation test
  (`test_no_lookahead_truncation`) confirms indicator and
  signal values at bar j are identical whether computed on
  the full frame or on the frame truncated at j.
- **Source check:** the original Pine v4 source (per the
  ProEA line-by-line read, verified live 2026-11-24) defines
  Buy as the close crossing above the trailing line — the
  `ema(src, 1)` in its `above = crossover(ema, xATRTrailingStop)`
  is the source itself, so `crossed_above(c, ut_stop)` is the
  faithful translation. The recursion's `nz(prev, 0)` seed
  matches the on-disk `prev = 0.0` fallback; the first-bar
  `stop = close − nLoss` matches the original's first-bar
  behaviour. No bug found, no code changed.
- **Tests:** 13/13 pass (`python3 -m unittest
  strategies.ut_bot.test_ut_bot`).
- **No parameter was tuned to PnL.** KeyValue stays 1.0.
