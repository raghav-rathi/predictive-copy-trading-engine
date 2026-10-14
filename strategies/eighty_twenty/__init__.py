"""80-20 momentum-candle fade engine: registration + re-exports."""

from strategies.eighty_twenty import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="80-20 Momentum-Candle Fade (Raschke)",
        slug="eighty_twenty",
        description=(
            "Fade exhaustion after 80th-percentile momentum candles: push "
            ">=0.5xATR past the momentum close then close back inside its "
            "range within 5 bars; 1.5xATR target, 2xATR stop, 24-bar max hold."
        ),
        source_name="Linda Raschke, Street Smarts (80-20)",
        source_url="https://roboforex.com/blog/education/trading-strategies-that-were-a-revolution-three-strategies-of-linda-raschke/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
