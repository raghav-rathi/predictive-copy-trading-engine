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
