"""Wyckoff distribution engine: registration + re-exports."""

from strategies.wyckoff_distribution import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Wyckoff Distribution",
        slug="wyckoff_distribution",
        description=(
            "Wyckoff distribution schematic, SHORT ONLY: after "
            "a >=5% advance over 120 bars, a UTAD (false "
            "breakout above the 120-bar high, close reclaimed "
            "within 3 bars) enters short; a sign of weakness "
            "(wide down bar closing below the range midpoint) "
            "followed by a last point of supply (lower-high "
            "pullback holding below the UTAD high) enters "
            "short again. Exit above utad_high or below the "
            "range projection; 2xATR stop, 3xATR trail, "
            "120-bar max hold."
        ),
        source_name="Wyckoff distribution schematic — Wyckoff method",
        source_url="https://www.cmcmarkets.com/en-gb/trading-strategy/what-is-wyckoff-method",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
