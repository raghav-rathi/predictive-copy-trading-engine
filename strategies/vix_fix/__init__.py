"""Larry Williams' VIX Fix fear-spike mean reversion: registration + re-exports."""

from strategies.vix_fix import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="VIX Fix Fear-Spike Mean Reversion",
        slug="vix_fix",
        description=(
            "Larry Williams' VIX Fix: WVF = 100*(Highest(High,22)-Low)/"
            "Highest(High,22) with a Bollinger Band (20, 2.0); long on a "
            "cross above the upper band (extreme fear spike), exit on a "
            "cross back below the midline; mirrored inverse iWVF leg for "
            "greed-spike shorts; 2xATR stop, 24-bar max hold."
        ),
        source_name="Larry Williams VIX Fix (pineify.app writeup)",
        source_url="https://pineify.app/resources/blog/cm-williams-vix-fix-finds-market-bottoms-indicator-tradingview-pine-script",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
