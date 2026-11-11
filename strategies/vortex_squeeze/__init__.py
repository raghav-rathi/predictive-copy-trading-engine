"""Vortex Squeeze: registration + re-exports."""

from strategies.vortex_squeeze import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Vortex Squeeze",
        slug="vortex_squeeze",
        description="Vortex Indicator VI+/VI- cross gated by a Bollinger BandWidth squeeze: trade the cross only while BandWidth(20,2) is below its 120-bar 20th percentile, or within 5 bars after the squeeze ends; exit on the opposite cross.",
        source_name="Vortex Indicator (Botes & Siepman, TASC Jan 2010); Bollinger BandWidth squeeze",
        source_url="https://www.investopedia.com/terms/v/vortex-indicator-vi.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
