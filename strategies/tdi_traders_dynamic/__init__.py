"""Traders Dynamic Index engine: registration + re-exports."""

from strategies.tdi_traders_dynamic import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Traders Dynamic Index",
        slug="tdi_traders_dynamic",
        description=(
            "Dean Malone's Traders Dynamic Index: RSI(13) with a "
            "2-bar price line, 7-bar signal line, 34-bar market base "
            "line and +/-1.6185 sigma volatility bands; long when the "
            "price line crosses above the signal line with price above "
            "base and base above 50, short on the mirror, exit on the "
            "opposite cross; 2xATR stop, 3xATR trail, 60-bar max hold."
        ),
        source_name="Dean Malone, Traders Dynamic Index (TDI)",
        source_url="https://www.quantum-algo.com/blog/guides/traders-dynamic-index-tdi/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
