"""RSI extreme-edge engine: registration + re-exports."""

from strategies.rsi_extreme_edge import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="RSI extreme-edge fade (RSI14 90/10 cross-back)",
        slug="rsi_extreme_edge",
        description=(
            "Fade RSI(14) exhaustion: short the cross back below 90, long "
            "the cross back above 10; 1.5xATR stop, 1.5xSL target, 72-bar "
            "max hold."
        ),
        source_name="@Vision33X / visioneth rsi-extreme-edge (138 live trades, 2026)",
        source_url="https://github.com/visioneth/rsi-extreme-edge",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
