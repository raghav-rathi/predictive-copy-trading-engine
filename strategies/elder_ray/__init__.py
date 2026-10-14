"""Elder Ray engine: registration + re-exports."""

from strategies.elder_ray import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Elder Ray Bull/Bear Power system",
        slug="elder_ray",
        description=(
            "Bull Power = H-EMA(13), Bear Power = L-EMA(13); long when the "
            "EMA rises and negative Bear Power turns up, short on the "
            "mirror; exit when the power crosses zero against the trade."
        ),
        source_name="Dr. Alexander Elder — Elder Ray (1989)",
        source_url="https://www.bajajfinserv.in/elder-ray-index-trading-strategy",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
