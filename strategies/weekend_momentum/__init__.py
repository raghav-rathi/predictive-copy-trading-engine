"""Weekend Crypto Momentum: registration + re-exports."""

from strategies.weekend_momentum import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Weekend Crypto Momentum",
        slug="weekend_momentum",
        description=(
            "168h momentum long/short gated to weekend sessions: enter "
            "Friday 00:00 UTC, exit at the Monday 00:00 UTC bar, flat "
            "on weekdays. Long when 168h momentum > 0, short when < 0. "
            "2xATR stop, 2xATR trail, 72-bar max hold."
        ),
        source_name="Advances in Consumer Research — The Weekend Effect in Crypto Momentum",
        source_url="https://acr-journal.com/article/the-weekend-effect-in-crypto-momentum-does-momentum-change-when-markets-never-sleep--1514/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
