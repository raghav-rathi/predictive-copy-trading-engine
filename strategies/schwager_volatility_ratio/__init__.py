"""Schwager volatility-ratio engine: registration + re-exports."""

from strategies.schwager_volatility_ratio import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Schwager Volatility Ratio",
        slug="schwager_volatility_ratio",
        description=(
            "Schwager VR = true range / EMA of prior true ranges (14); "
            "fade wide bars (VR > 2.0): long a bearish wide bar closing "
            "in its lower quarter with a negative 5-bar return, short "
            "the mirror; exit on the opposite wide bar, a 1.5R target, "
            "or a 10-bar time exit; 2xATR stop (approx. beyond the wide "
            "bar's extreme), 3xATR target, 10-bar max hold."
        ),
        source_name="Schwager Volatility Ratio",
        source_url="https://www.incrediblecharts.com/indicators/volatility_ratio_schwager.php",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
