"""NR7 Breakout: registration + re-exports."""

from strategies.nr7_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="NR7 Breakout",
        slug="nr7_breakout",
        description=(
            "Toby Crabel's Narrow Range 7: the bar whose high-low range is the narrowest of the last 7 bars marks volatility contraction. Long on a close above the NR7 bar's high, short below its low, valid for 24 bars after the NR7 bar. 2xATR stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="NR7 (Toby Crabel)",
        source_url="https://therobusttrader.com/title-nr7-trading-strategy-the-narrow-range-7-by-toby-crabel/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
