"""Volume Spike Breakout: registration + re-exports."""

from strategies.volume_spike_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Volume Spike Breakout",
        slug="volume_spike_breakout",
        description=(
            "20-bar high/low breakout confirmed by volume over twice its 20-bar average; exit on the opposite breakout."
        ),
        source_name="Volume-confirmed breakout (Murphy; Bulkowski, Encyclopedia of Chart Patterns)",
        source_url="https://www.investopedia.com/terms/v/volume.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
