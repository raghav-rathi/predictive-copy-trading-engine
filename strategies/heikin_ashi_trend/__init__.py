"""Heikin Ashi trend: registration + re-exports."""

from strategies.heikin_ashi_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Heikin Ashi Trend",
        slug="heikin_ashi_trend",
        description="Heikin Ashi trend (Dan Valcu, 2004): long after 2 consecutive green Heikin Ashi candles following a red run while the real close is above EMA(50) of real closes; short mirror. Exit on the first opposite-colour Heikin Ashi candle. Stops are on real prices via the risk layer, never on HA values.",
        source_name="Heikin Ashi trading strategy (Dan Valcu)",
        source_url="https://bjftradinggroup.com/heikin-ashi-trading-strategy/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
