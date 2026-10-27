"""Bat Harmonic Pattern: registration + re-exports."""

from strategies.bat_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Bat Harmonic Pattern",
        slug="bat_pattern",
        description=(
            "Scott Carney Bat (2001) XABCD: AB 38.2–50% of XA, BC 38.2–88.6% of AB, CD 161.8–261.8% of BC, AD 88.6% of XA (±6%); bullish Bat buys the D completion, bearish sells it. Same causal zigzag engine as harmonic_gartley, different ratio stack."
        ),
        source_name="Scott Carney Bat harmonic pattern (Harmonic Trading, 2001)",
        source_url="https://www.investmacro.com/forex/2016/12/harmonic-trading-patterns-from-scott-m-carney-explained-in-detail/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
