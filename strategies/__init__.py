"""Technical trading strategy engines — long/short signal library.

Each subpackage implements ONE verifiable strategy:
    strategies/<slug>/indicators.py  -- indicator computation (pure pandas/numpy)
    strategies/<slug>/signals.py      -- entry/exit signal logic
    strategies/<slug>/risk.py         -- stops, trailing, targets, sizing config
    strategies/<slug>/test_<slug>.py  -- unit tests (must be green)
    strategies/<slug>/BACKTEST.md     -- empirical validation on real Hyperliquid candles

Shared infra:
    strategies/base.py      -- signal conventions + Engine protocol
    strategies/data.py      -- Hyperliquid candle loader + disk cache
    strategies/backtest.py  -- event-driven backtest harness (fees, slippage, funding)
    strategies/registry.py  -- strategy registry

Paper-first: everything runs on historical candles / paper signals only.
No live execution is wired anywhere in this package by design.
"""
