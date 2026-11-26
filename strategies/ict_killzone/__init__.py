"""ICT killzone engine: registration + re-exports."""

from strategies.ict_killzone import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="ICT Killzone",
        slug="ict_killzone",
        description=(
            "ICT killzones: Asian-range (00:00-03:00 UTC) sweep "
            "during the London (07:00-10:00 UTC) or NY "
            "(12:00-14:00 UTC) killzone, >=1.0x ATR displacement "
            "breaking market structure, then entry on a "
            "retracement to the 50% level of the displacement leg "
            "(FVG-midpoint approximation); 2xATR stop, 3xATR "
            "trail, 24-bar max hold."
        ),
        source_name="ICT kill zones — ictkillzone.com / Audacity Capital",
        source_url="https://www.ictkillzone.com/ict-kill-zones",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
