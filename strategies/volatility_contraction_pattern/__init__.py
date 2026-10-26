"""Volatility Contraction Pattern (VCP): registration + re-exports."""

from strategies.volatility_contraction_pattern import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Volatility Contraction Pattern (VCP)",
        slug="volatility_contraction_pattern",
        description=(
            "Minervini VCP operationalized on 1h bars: uptrend + falling ATR + tight range, then a breakout above the 20-bar high on expanding volume. Long only."
        ),
        source_name="Mark Minervini volatility contraction pattern (Trade Like a Stock Market Wizard)",
        source_url="https://www.makecade.com/guides-minervini-vcp.html",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
