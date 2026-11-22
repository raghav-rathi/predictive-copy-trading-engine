"""StatOasis Rule 4: Multi-Indicator Momentum — registration + re-exports."""

from strategies.base import StrategySpec
from strategies.statoasis_rule4_momentum import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="StatOasis Rule 4: Multi-Indicator Momentum",
        slug="statoasis_rule4_momentum",
        description=(
            "StatOasis AI Rule 4, adapted from daily SPY to 1h "
            "crypto: LONG when RSI(14) > 55 AND Stochastic %K(14, "
            "smooth 3) > 50 AND Williams %R(14) > -50 AND 120h return "
            "> 1%, with a fixed 10-bar time exit and no indicator "
            "exit. Short side is a builder-added mirror. 2xATR stop, "
            "no trail, 10-bar max hold."
        ),
        source_name="StatOasis — Can AI Build a Profitable Trading Strategy? 5 Rules Tested (Rule 4)",
        source_url="https://statoasis.com/overfit/research/ai-strategy-validation",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
