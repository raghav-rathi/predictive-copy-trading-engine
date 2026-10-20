"""Ross Hook Continuation: registration + re-exports."""

from strategies.ross_hook import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ross Hook Continuation",
        slug="ross_hook",
        description=(
            "Joe Ross 1-2-3 + Hook on 5-bar fractal pivots: P1 pivot low, "
            "P2 pivot high, P3 higher pivot low; long on a close above P2 "
            "(breakout) then a close above the first pivot high that holds "
            "above P3 (the hook); mirror for shorts. 1.5xATR stop, "
            "2.5xATR target, 60-bar max hold."
        ),
        source_name="Ross Hook (Joe Ross, via theforexgeek.com)",
        source_url="https://theforexgeek.com/ross-hook-pattern/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
