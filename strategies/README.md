# Technical Strategy Library — batch 4 (2026-10-13)

Twelve real, tested, empirically-validated signal engines on
`feat/strat-iter-20261013-a`, merged from three build batches (a/b/c).
Each strategy is a self-contained subpackage:

    strategies/<slug>/indicators.py   -- indicator computation (pure pandas/numpy)
    strategies/<slug>/signals.py       -- entry/exit signal logic
    strategies/<slug>/risk.py         -- stops, trailing, targets, sizing config
    strategies/<slug>/test_<slug>.py  -- unit tests (green)
    strategies/<slug>/BACKTEST.md     -- empirical validation on Hyperliquid 1h candles
    strategies/<slug>/CALIBRATION.md  -- parameter sweep notes

Shared infra in this branch: `base.py` (signal conventions, indicator
primitives, `RiskConfig`/`StrategySpec`), `registry.py`, `data.py`
(Hyperliquid candle loader + disk cache), `backtest.py` (event-driven
harness: fees, slippage, funding; no lookahead), `tests/test_infra.py`.

Paper-first: everything runs on historical candles / paper signals only.
No live execution is wired anywhere in this package by design.

See STRATEGY_SUMMARY.md for the batch scorecard.

---

# Batch 5 (2026-10-14) — named-author classic-indicator sweep

Ten more signal engines on `feat/strat-iter-20261014-momentum`, all from
documented, named-author mechanisms: `coppock_curve` (E.S. Coppock),
`smi_ergodic` (Blau), `klinger_oscillator` (Klinger), `qstick` (Chande),
`rsi_bollinger` (Bollinger-on-RSI mean reversion), `cmf_trend` (Chaikin),
`chande_cmo` (Chande), `elder_ray` (Elder), `dpo_cycle` (ChartSchool),
`pgo` (Mark Johnson). Same subpackage layout; 510 tests green
(full suite incl. prior batches). Backtests on Hyperliquid 1h candles
(BTC/ETH/HYPE, 2026-03-20 → 2026-10-14): Coppock wins on HYPE (+50.2%,
Sharpe 2.61); the other nine lose — Qstick worst (−$17,746), RSI+Bollinger
the high-win-rate trap (47% WR, −$13,075). Honest losers recorded in
each BACKTEST.md.

Shared infra change in this batch: `base.crossed_above`/`crossed_below`
now accept scalar levels (broadcast to the series index); Series behavior
unchanged.
