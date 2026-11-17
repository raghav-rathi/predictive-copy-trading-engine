"""Volume-confirmed breakout: registration + re-exports."""

from strategies.volume_ma_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Volume MA Breakout",
        slug="volume_ma_breakout",
        description="Classic volume-confirmed breakout: long on a new 20-bar high with volume > 1.5x the trailing 20-bar mean volume (previous 20 bars), short on a new 20-bar low with the same volume confirmation. Exit long on a close below the trailing 10-bar low (prior 10 bars), exit short on a close above the trailing 10-bar high, plus the harness stop/trail.",
        source_name="Classic volume-confirmed breakout (Donchian-style range breakout with volume confirmation)",
        source_url="",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
