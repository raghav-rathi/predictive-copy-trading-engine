"""Cup and Handle Breakout: registration + re-exports."""

from strategies.cup_handle import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Cup and Handle Breakout",
        slug="cup_handle",
        description=(
            "William O'Neil's cup and handle on 1h bars: prior uptrend "
            "(close > SMA50 for 30 bars), a 60-300 bar cup 8-25% deep "
            "(1-4xATR) with the right rim within 5% of the left, a shallow "
            "handle in the cup's upper half, and entry on a close above the "
            "handle high with volume > 1.4x the 20-bar average. Long-only; "
            "1.5xATR stop, 4.0xATR target, 120-bar max hold."
        ),
        source_name="Cup and Handle (O'Neil, via ebc.com)",
        source_url="https://www.ebc.com/forex/cup-and-handle-pattern-how-to-use-in-forex-trading",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
