"""ZigZag Swing Breakout: registration + re-exports."""

from strategies.zigzag_swing import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="ZigZag Swing Breakout",
        slug="zigzag_swing",
        description=(
            "ZigZag swing breakout (5% deviation): confirmed swing highs/lows from a causal pivot tracker; long on close above the last swing high, short below the last swing low."
        ),
        source_name="ZigZag swing indicator (classic charting)",
        source_url="https://school.stockcharts.com/doku.php?id=technical_indicators:zigzag",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
