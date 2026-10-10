"""Dual Thrust engine: registration + re-exports."""

from strategies.dual_thrust import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Dual Thrust (Chalek session-range breakout)",
        slug="dual_thrust",
        description=(
            "BuyLine=day open+0.7*max(HH-LC,HC-LL) over 5 prior sessions; "
            "reversing breakout system."
        ),
        source_name="Dual Thrust (Michael Chalek) — FMZ Quant implementation writeup",
        source_url="https://steemit.com/fmz/@fmz.com/implementation-of-dual-thrust-trading-algorithm-by-using-mylanguage-on-fmz-quant-platform",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
