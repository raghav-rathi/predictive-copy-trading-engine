"""Camarilla pivots engine: registration + re-exports."""

from strategies.camarilla_pivots import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Camarilla pivots (fade default)",
        slug="camarilla_pivots",
        description=(
            "Nick Stott Camarilla levels from the prior 24h-UTC session: "
            "fade mode shorts first R3 touch / longs first S3 touch targeting "
            "the pivot mid; breakout mode goes stop-and-reverse on closes "
            "beyond R4/S4."
        ),
        source_name="Nick Stott Camarilla pivots",
        source_url="https://www.fxstreet.com/amp/education/trading-stocks-with-camarilla-pivots-201211010000",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
