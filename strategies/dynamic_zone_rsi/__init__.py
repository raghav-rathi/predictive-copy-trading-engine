"""Dynamic Zones RSI engine: registration + re-exports."""

from strategies.dynamic_zone_rsi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Dynamic Zones RSI",
        slug="dynamic_zone_rsi",
        description=(
            "Dynamic Zones (Zamansky & Stendahl 1996): RSI(14) with "
            "adaptive zones -- buy zone = 12th percentile of RSI over "
            "rolling 70 bars, sell zone = 88th percentile; long when "
            "RSI crosses back above the buy zone after dipping below "
            "it, short when RSI crosses back below the sell zone after "
            "exceeding it; exits at RSI crossing 50 or opposite zone "
            "touch; 2xATR stop, 3xATR chandelier trail, 120-bar max hold."
        ),
        source_name="Dynamic Zones (Zamansky & Stendahl, S&C July 1996 V15:7)",
        source_url="https://www.tradingview.com/script/AoChfBer-How-To-Use-Dynamic-Zones/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
