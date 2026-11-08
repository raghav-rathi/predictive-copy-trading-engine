"""Rolling volume-profile POC: registration + re-exports."""

from strategies.volume_profile_poc import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Volume Profile POC",
        slug="volume_profile_poc",
        description="Rolling 168-bar volume profile: POC is the midpoint of the highest-volume bin of 24 equal price bins, VAH/VAL bound the smallest contiguous bin set around POC holding >=70% of window volume; enter long on a pullback dip to within 0.5x ATR of POC that closes back above POC (prior close above POC), mirror for shorts; exit at VAH/VAL or on a close back through POC.",
        source_name="PriceActionNinja — POC Trading Strategy",
        source_url="https://priceactionninja.com/poc-trading-strategy/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
