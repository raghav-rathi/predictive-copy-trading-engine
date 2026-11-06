"""Volume-weighted MACD: registration + re-exports."""

from strategies.volume_weighted_macd import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Volume-weighted MACD",
        slug="volume_weighted_macd",
        description="MACD (12/26/9) computed on a 20-bar volume-weighted price series (rolling sum of close*volume over rolling sum of volume), with a SMA(50) trend filter: long on a MACD cross above its signal line with a positive histogram while the volume-weighted price is above SMA(50); short on the mirror.",
        source_name="Volume-weighted MACD",
        source_url="",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
