"""Pairs Spread (BTC-ETH): registration + re-exports."""

from strategies.pairs_spread import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Pairs Spread (BTC-ETH)",
        slug="pairs_spread",
        description="Gatev, Goetzmann & Rouwenhorst (2006) pairs trading on BTC vs ETH: spread = log(BTC) - beta * log(ETH) with beta the rolling 500-bar OLS hedge ratio; z = (spread - 100-bar mean) / 100-bar std. Long the spread (long BTC / short ETH) when z crosses below -2, short the spread when z crosses above +2, exit at z crossing 0. Backtested as a single synthetic spread book.",
        source_name="Gatev, Goetzmann & Rouwenhorst — Pairs Trading: Performance of a Relative-Value Arbitrage Rule (2006)",
        source_url="https://doi.org/10.1093/rfs/hhj020",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
