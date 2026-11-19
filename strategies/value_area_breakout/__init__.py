"""Value-area breakout: registration + re-exports."""

from strategies.value_area_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Value-Area Breakout",
        slug="value_area_breakout",
        description="Volume-profile value-area breakout on the prior UTC day's profile (50 bins, 70% value area): long on the 2nd consecutive close above VAH, short on the 2nd consecutive close below VAL; exit on a close back inside the value area or opposite acceptance, plus the harness stop/trail.",
        source_name="Volume Profile Trading Strategy (Trading Strategy Guides)",
        source_url="https://tradingstrategyguides.com/volume-profile-trading-strategy/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
