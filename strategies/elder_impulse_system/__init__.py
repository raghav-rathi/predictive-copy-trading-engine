"""Elder Impulse System: registration + re-exports."""

from strategies.elder_impulse_system import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Elder Impulse System",
        slug="elder_impulse_system",
        description="Elder Impulse System (Alexander Elder, 2002): green bar = EMA(13) rising AND MACD histogram (12,26,9) rising; red bar = both falling; blue = disagreement. Long on the first green bar after a red/blue bar; short on the first red bar after a green/blue bar; exit long on a red or blue bar, exit short on a green or blue bar.",
        source_name="Elder Impulse System (Alexander Elder)",
        source_url="https://www.chartlearning.com/2021/05/elder-impulse-trading-system.html",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
