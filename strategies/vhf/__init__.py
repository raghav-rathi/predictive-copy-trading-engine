"""VHF Trend Regime: registration + re-exports."""

from strategies.vhf import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="VHF Trend Regime",
        slug="vhf",
        description=(
            "Adam White Vertical Horizontal Filter (28 bars): (highest high - lowest low) / sum |close changes|; enter in the direction of price vs SMA(28) when VHF crosses above 0.45, exit when it falls below 0.35."
        ),
        source_name="Vertical Horizontal Filter (Adam White, Futures 1991)",
        source_url="https://www.incrediblecharts.com/indicators/vertical_horizontal_filter.php",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
