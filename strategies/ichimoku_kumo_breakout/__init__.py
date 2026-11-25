"""Ichimoku Kumo breakout engine: registration + re-exports."""

from strategies.ichimoku_kumo_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ichimoku Kumo Breakout",
        slug="ichimoku_kumo_breakout",
        description=(
            "Goichi Hosoda's Ichimoku Kumo (cloud) breakout: long "
            "when close crosses above the cloud top with tenkan > "
            "kijun, short when close crosses below the cloud bottom "
            "with tenkan < kijun, exit when close comes back into "
            "the cloud; chikou span never read (lookahead); 2xATR "
            "stop, 3xATR trail, 120-bar max hold."
        ),
        source_name='Wikipedia, "Ichimoku Kinkō Hyō"',
        source_url="https://en.wikipedia.org/wiki/Ichimoku_Kink%C5%8D_Hy%C5%8D",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
