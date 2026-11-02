"""Keltner Breakout: registration + re-exports."""

from strategies.keltner_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Keltner Breakout",
        slug="keltner_breakout",
        description=(
            "Keltner channel breakout: EMA(20) +/- 2xATR(10); long on close above the upper band, short below the lower band, exit on return to the midline."
        ),
        source_name="Keltner channels (Chester Keltner)",
        source_url="https://school.stockcharts.com/doku.php?id=technical_indicators:keltner_channels",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
