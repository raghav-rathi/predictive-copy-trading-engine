"""Ichimoku Tenkan/Kijun cross: registration + re-exports."""

from strategies.tenkan_kijun_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Ichimoku Tenkan/Kijun Cross",
        slug="tenkan_kijun_cross",
        description="Ichimoku Tenkan-sen(9) crossing Kijun-sen(26): long on a cross up, short on a cross down, exit on the opposite cross. Trades the two lines crossing each other — distinct from kijun_cross, which trades the close crossing the Kijun-sen. No cloud, price, or Chikou filter.",
        source_name="BabyPips — Ichimoku Kinko Hyo",
        source_url="https://www.babypips.com/learn/forex/ichimoku-kinko-hyo",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
