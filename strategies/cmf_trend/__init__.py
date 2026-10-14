"""Chaikin Money Flow engine: registration + re-exports."""

from strategies.cmf_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Chaikin Money Flow zero-cross system",
        slug="cmf_trend",
        description=(
            "CMF(21) = sum(CLV*V)/sum(V); long when it crosses above zero "
            "with close above its 200-bar SMA, short on the mirror; exit on "
            "the opposite zero cross."
        ),
        source_name="Marc Chaikin — Chaikin Money Flow",
        source_url="https://www.tradingview.com/scripts/chaikinmoneyflow/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
