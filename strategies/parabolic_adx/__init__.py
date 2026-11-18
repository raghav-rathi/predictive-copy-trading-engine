"""Parabolic ADX: registration + re-exports."""

from strategies.parabolic_adx import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Parabolic ADX",
        slug="parabolic_adx",
        description="Parabolic SAR(0.02, 0.20) flip gated by ADX(14): long on a PSAR flip below price with ADX > 25 and +DI > -DI, short on the mirror flip; exit on the opposite PSAR flip or ADX < 20, plus the harness stop/trail.",
        source_name="Combining Parabolic SAR with ADX (Unofficed)",
        source_url="https://unofficed.com/courses/mastering-market-indicators/lessons/combining-parabolic-sar-with-adx/?ld-lesson-page=2",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
