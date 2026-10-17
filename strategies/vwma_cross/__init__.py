"""VWMA-cross engine: registration + re-exports."""

from strategies.vwma_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="VWMA(20/50) volume-conviction cross system",
        slug="vwma_cross",
        description=(
            "Typical-price VWMA(20) vs VWMA(50) cross, gated on volume "
            "above its 20-bar average; exit on the cross back."
        ),
        source_name="Volume-weighted MA cross (volume-confirmed trend)",
        source_url="https://www.investopedia.com/terms/v/vwma.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
