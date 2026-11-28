"""AO Saucer engine: registration + re-exports."""

from strategies.ao_saucer import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="AO Saucer (Bill Williams)",
        slug="ao_saucer",
        description=(
            "Bill Williams Awesome Oscillator Saucer: AO = "
            "SMA(median, 5) - SMA(median, 34). A buy saucer "
            "is three AO bars above zero with the middle bar "
            "falling (red) and the last bar rising (green); "
            "a sell saucer is the mirror below zero. Exit "
            "on an AO zero-cross or the opposite saucer; "
            "2xATR stop, 3xATR trail, 96-bar max hold."
        ),
        source_name="Awesome Oscillator Saucer — Bill Williams, New Trading Dimensions",
        source_url="https://www.mql5.com/en/code/13",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
