"""Raschke Anti engine: registration + re-exports."""

from strategies.raschke_anti import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name='Raschke & Connors "Anti" (3/10/16)',
        slug="raschke_anti",
        description=(
            'Linda Raschke "Anti" (Street Smarts Ch.9): trend defined by '
            "slow-stochastic %D slope; enter after a counter-move (%K hook "
            "or 2-bar inside day) when 3/10 crosses back above its 16-signal "
            "or %K re-aligns. 2xATR stop, 3xATR trailing."
        ),
        source_name='Raschke & Connors, Street Smarts Ch.9 "Anti"',
        source_url="https://theforexgeek.com/linda-raschkes-macd-3-10-16-strategy/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
