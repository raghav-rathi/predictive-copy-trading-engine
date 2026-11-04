"""Outside Bar Breakout: registration + re-exports."""

from strategies.outside_bar_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Outside Bar Breakout",
        slug="outside_bar_breakout",
        description="Outside (engulfing-range) bar breakout: a bar whose high exceeds the prior bar's high AND whose low undercuts the prior bar's low, closing in the top (bullish) or bottom (bearish) third of its range. Entry on the next bar's close beyond the outside bar's extreme; exit on an opposite outside bar.",
        source_name="Outside Bar (engulfing-range) breakout",
        source_url="https://www.luxalgo.com/library/concept/outside-bar/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
