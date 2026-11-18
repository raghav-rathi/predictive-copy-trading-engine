"""Supertrend Parabolic: registration + re-exports."""

from strategies.supertrend_parabolic import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Supertrend Parabolic",
        slug="supertrend_parabolic",
        description="Supertrend(10, 3.0) + Parabolic SAR(0.02, 0.20) agreement: long on the bar price becomes above both lines, short on the bar it becomes below both; exit when price crosses either line against the trade, plus the harness stop/trail.",
        source_name="Applying the Parabolic SAR and the Supertrend (About Trading, Substack)",
        source_url="https://abouttrading.substack.com/p/applying-the-parabolic-sar-and-the",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
