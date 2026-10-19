"""Murrey Math octave extreme-reversal engine: registration + re-exports."""

from strategies.murray_math import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Murrey Math Octave Reversal",
        slug="murray_math",
        description=(
            "Trailing 64-bar high/low frame split into 8 Murrey octaves "
            "(L0=[0/8] ... L8=[8/8], 4/8 pivot); long on a bottom-zone "
            "(0/8-1/8) touch followed by a close back above L1, short on a "
            "top-zone (7/8-8/8) touch followed by a close back below L7; "
            "exits at the 4/8 pivot or the opposite extreme touch; "
            "2xATR stop, 80-bar max hold."
        ),
        source_name="Murrey Math Lines v6 (TradingView)",
        source_url="https://th.tradingview.com/script/Lm6H0fRT-Murrey-Math-Lines-v6/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
