"""Elliott wave-count engine: registration + re-exports."""

from strategies.elliott_wave_count import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Elliott Wave Count",
        slug="elliott_wave_count",
        description=(
            "Strict mechanical Elliott count over 5-bar pivots: wave 2 "
            "must retrace 38.2-61.8% of wave 1, wave 3 is never the "
            "shortest (checked at the wave-4 pivot), wave 4 never "
            "overlaps wave-1 territory; enter long on a close above "
            "the wave-1 high (wave-3 breakout), exit on invalidation "
            "or the 161.8% wave-5 extension target; 2xATR stop (approx. "
            "the wave-2 extreme), 3xATR target, 96-bar max hold."
        ),
        source_name="Elliott Wave Theory",
        source_url="https://www.rabofund.com/blogs/what-is-elliott-wave-theory-a-practical-guide-for-forex-traders",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
