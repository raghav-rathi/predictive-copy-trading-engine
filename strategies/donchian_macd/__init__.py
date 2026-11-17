"""Donchian MACD: registration + re-exports."""

from strategies.donchian_macd import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Donchian MACD",
        slug="donchian_macd",
        description="Donchian(20) channel breakout confirmed by MACD(12,26,9): long on a close above the trailing 20-bar high with MACD histogram > 0, short on a close below the trailing 20-bar low with histogram < 0; exit on the opposite channel break or a histogram flip, plus the harness stop/trail.",
        source_name="Donchian channel + MACD confirmation (batch-38 spec, no external source supplied)",
        source_url="",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
