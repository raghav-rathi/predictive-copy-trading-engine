"""Opening-range breakout-failure fade engine: registration + re-exports."""

from strategies.orb_fade import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Opening Range Breakout Failure Fade",
        slug="orb_fade",
        description=(
            "Opening range breakout failure fade: the UTC-day "
            "opening range is the high/low of the first 4 bars "
            "(00:00-03:00 UTC); a close crossing above or_high "
            "or below or_low breaks the range, and a close back "
            "inside within 6 bars fades the break (short after "
            "a failed upside break, long after a failed "
            "downside break). Exit on a close back beyond the "
            "frozen range level or the opposite fade entry; "
            "2xATR stop, 3xATR trail, 24-bar max hold."
        ),
        source_name="Opening range breakout failure fade — ORB failure",
        source_url="https://steady-turtle.com/knowledge/opening-range-breakout-strategy",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
