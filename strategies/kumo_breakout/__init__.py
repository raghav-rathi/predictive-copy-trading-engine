"""Kumo Breakout: registration + re-exports."""

from strategies.kumo_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Kumo Breakout",
        slug="kumo_breakout",
        description=(
            "Ichimoku Kumo breakout: close crosses above the cloud top (max of Senkou A/B) for longs, below the cloud bottom for shorts; exit on re-entering the cloud."
        ),
        source_name="Ichimoku Cloud / Kumo breakout",
        source_url="https://school.stockcharts.com/doku.php?id=technical_indicators:ichimoku_cloud",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
