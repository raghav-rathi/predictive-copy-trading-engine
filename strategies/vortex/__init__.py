"""Vortex engine: registration + re-exports."""

from strategies.vortex import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Vortex (ADX-confirmed)",
        slug="vortex",
        description=(
            "Vortex indicator VI+/VI- crosses (Botes & Siepman, S&C Jan 2010) "
            "for entries/exits, gated by ADX(14) > 20; 2.5xATR hard stop."
        ),
        source_name="Botes & Siepman, 'The Vortex Indicator', S&C Jan 2010",
        source_url="https://www.Markets.com/pt/education-centre/vortex-indicator/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
