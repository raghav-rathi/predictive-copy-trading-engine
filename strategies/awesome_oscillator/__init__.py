"""Awesome Oscillator engine: registration + re-exports."""

from strategies.awesome_oscillator import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Awesome Oscillator (Williams)",
        slug="awesome_oscillator",
        description=(
            "AO = SMA5-SMA34 of median price; entries on zero-cross, "
            "saucer, and twin-peaks; exits on opposite cross; 2xATR "
            "stop, 72-bar max hold."
        ),
        source_name="Awesome Oscillator (Bill Williams) — MetaTrader 5 docs",
        source_url="https://www.metatrader5.com/en/terminal/help/indicators/bw_indicators/awesome",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
