"""Volatility Breakout: registration + re-exports."""

from strategies.volatility_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Volatility Breakout",
        slug="volatility_breakout",
        description=(
            "Larry Williams volatility breakout on 1h bars: long when close clears the prior close plus half the prior bar's range, short on the mirror, exit on the opposite break."
        ),
        source_name="Larry Williams volatility breakout (Long-Term Secrets to Short-Term Trading)",
        source_url="https://www.mql5.com/en/articles/20745",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
