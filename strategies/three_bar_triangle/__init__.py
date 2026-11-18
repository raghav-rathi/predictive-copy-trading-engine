"""Raschke 3-bar triangle: registration + re-exports."""

from strategies.three_bar_triangle import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Raschke 3-Bar Triangle",
        slug="three_bar_triangle",
        description="Linda Raschke 3-bar triangle: an inside-bar contraction (high below the prior two bars' high, low above their low) defines a 3-bar triangle; long on a close above the triangle high with volume > 1.25x its 20-bar average within 5 bars (short is the mirror); exit on a close back through the far triangle edge or the opposite signal, plus the harness stop/trail.",
        source_name="Raschke 3-bar triangle (New Trader U; cTrader)",
        source_url="https://www.newtraderu.com/2022/08/25/market-wizard-linda-raschke-trading-strategy/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
