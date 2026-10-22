"""Ulcer Index regime-gated breakout: registration + re-exports."""

from strategies.ulcer_index import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ulcer Index Regime Gate",
        slug="ulcer_index",
        description=(
            "Ulcer Index (Peter Martin, 1987): sqrt(mean(percent-drawdown^2)) "
            "over 14 bars — a pure downside-volatility gauge. LONG-ONLY: "
            "buy when ulcer < 5.0 (calm regime) and close crosses above the "
            "prior 20-bar Donchian high; exit on a cross below the prior "
            "10-bar Donchian low OR a panic spike of ulcer > 10.0; "
            "1.5xATR stop, 2xATR chandelier trail, 120-bar max hold."
        ),
        source_name="Ulcer Index (Peter Martin, 1987)",
        source_url="https://en.wikipedia.org/wiki/Ulcer_index",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
