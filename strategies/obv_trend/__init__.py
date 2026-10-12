"""OBV trend engine: registration + re-exports."""

from strategies.obv_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="OBV Trend (Granville)",
        slug="obv_trend",
        description=(
            "On-Balance Volume trend: long when close > EMA(50), OBV > its "
            "EMA(20) and OBV rising; short mirrored; exit on EMA(50) cross "
            "against the position or OBV rollover."
        ),
        source_name="On-Balance Volume (Joseph Granville) — Investopedia",
        source_url="https://www.investopedia.com/terms/o/onbalancevolume.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
