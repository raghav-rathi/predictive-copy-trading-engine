"""Blau Double Smoothed Stochastic: registration + re-exports."""

from strategies.blau_dss import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Blau Double Smoothed Stochastic",
        slug="blau_dss",
        description=(
            "William Blau Double Smoothed Stochastic (21, 3, 3): stochastic %K double-smoothed with EMAs and traded against its 3-bar EMA trigger. Long on DSS cross above trigger, short on cross below; exits on the opposite cross."
        ),
        source_name="Double Smoothed Stochastic (William Blau)",
        source_url="https://school.stockcharts.com/doku.php?id=technical_indicators:double_smoothed_stochastic",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
