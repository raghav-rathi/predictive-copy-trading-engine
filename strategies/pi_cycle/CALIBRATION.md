# Pi Cycle Top — Calibration

Multiplier sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-11-24, batch-45
frozen window `[1773525600000, 1795525200000)`, same costs/sizing,
2xATR stop, 3xATR trail, no max hold). The multiplier is the
strategy's natural knob: it sets how far SMA(111) must stretch
above SMA(350) to call a top — 1.9 is looser (earlier top
calls), 2.1 is stricter. The sweep re-runs
`add_indicators(df, mult=X)` + `add_signals(df)` only — risk is
unchanged. Re-run for batch 45; the Nov-14 sweep is superseded.

| multiplier | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 1.9 | BTC | 0 | — | $0.00 | 0.00 | — | — |
| 1.9 | ETH | 0 | — | $0.00 | 0.00 | — | — |
| 1.9 | HYPE | 0 | — | $0.00 | 0.00 | — | — |
| 2.0 (shipped) | BTC | 0 | — | $0.00 | 0.00 | — | — |
| 2.0 (shipped) | ETH | 0 | — | $0.00 | 0.00 | — | — |
| 2.0 (shipped) | HYPE | 0 | — | $0.00 | 0.00 | — | — |
| 2.1 | BTC | 0 | — | $0.00 | 0.00 | — | — |
| 2.1 | ETH | 0 | — | $0.00 | 0.00 | — | — |
| 2.1 | HYPE | 0 | — | $0.00 | 0.00 | — | — |

Peak SMA(111)/SMA(350) ratio in the batch-45 window: BTC 1.13,
ETH 1.17, HYPE 1.22 (same as the Nov-14 window to two decimals —
the extra ten days added no ratio extremes).

## One-line verdict

- **1.9 / 2.0 / 2.1:** all identical — zero trades on every coin.
  The knob is completely flat because the peak SMA(111)/SMA(350)
  ratio in the window is only 1.13 (BTC), 1.17 (ETH), 1.22 (HYPE):
  even the loosest setting sits 0.7+ of ratio away from firing.
  The multiplier is not the problem — the 1h timeframe is.
- **Shipped decision:** keep the specified multiplier=2.0 as the
  registry config regardless. It was fixed before any backtest was
  run, and there is no in-sample signal to adopt from anyway. The
  honest read: this calibration sweep measures nothing except the
  distance between the observed ratio range and the threshold, and
  that distance says the strategy needs daily bars over multi-year
  data to be evaluated at all.

## Batch-45 audit (no code changes)

Lookahead audit of indicators.py / signals.py / risk.py against
`strategies/base.py`: SMA columns are trailing rolling means
(`min_periods=n`, data through bar j only); crosses use
`crossed_above`/`crossed_below`, which compare bar j against
`shift(1)` — no future data anywhere. The truncation test
(`test_no_lookahead_truncation`) passes. No bug was found, so no
code was changed and no parameter was tuned. The only edit in
batch 45 was filling in the empty `source_url` in `__init__.py`
with https://charts.perly.io/chart/pi-cycle (a live Pi Cycle Top
chart attributing the indicator to Philip Swift, verified via
web search 2026-11-24).
