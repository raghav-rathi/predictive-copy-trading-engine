"""Holy Grail engine: registration + re-exports."""

from strategies.holy_grail import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Holy Grail (Raschke/Connors)",
        slug="holy_grail",
        description=(
            "Street Smarts 'Holy Grail': ADX(14) > 30 and rising, first "
            "pullback touching the 20 EMA, buy stop above the touch bar, "
            "swing-low stop; one signal per ADX turn-up."
        ),
        source_name="Linda Raschke & Larry Connors, Street Smarts Ch.10",
        source_url="https://medium.com/mudrex/the-holy-grail-trading-strategy-1668bacf99a2",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
