"""Ichimoku engine: registration + re-exports."""

from strategies.ichimoku import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ichimoku Cloud (classic)",
        slug="ichimoku",
        description=(
            "Price vs cloud regime + Tenkan/Kijun cross trigger + Chikou "
            "confirmation; exits on TK cross or Kijun break; 2.5xATR stop."
        ),
        source_name="Goichi Hosoda Ichimoku (public rules)",
        source_url="https://www.investopedia.com/terms/i/ichimoku-cloud.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
