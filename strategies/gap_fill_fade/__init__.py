"""Gap Fill Fade: registration + re-exports.

Classic gap-fill mean reversion (Bulkowski, Encyclopedia of
Chart Patterns): fade a >= 0.5 ATR overnight-style gap on the
1h bar, expecting a fill back to the prior bar's close. LONG
on a gap down, SHORT on a gap up; one fade per gap. Exit on
the fill or the opposite gap. 2xATR(14) stop, 24-bar max hold,
no trail, no target.
"""

from strategies.base import StrategySpec
from strategies.gap_fill_fade import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Gap Fill Fade",
        slug="gap_fill_fade",
        description=(
            "Gap-fill mean reversion: LONG when bar i gaps down "
            "by >= 0.5 ATR(14) vs bar i-1's close (fade the gap, "
            "expecting a fill back up to prev_close); SHORT on the "
            "mirror gap up. One fade per gap, fired on the gap bar "
            "itself. Exit on the fill (close >= prev_close for "
            "longs, <= for shorts) or the opposite gap. 2xATR(14) "
            "stop, 24-bar max hold, no trail, no target."
        ),
        source_name="Gap-fill mean reversion (Bulkowski, Encyclopedia of Chart Patterns)",
        source_url="https://thepatternsite.com/GaugingGaps.html",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
