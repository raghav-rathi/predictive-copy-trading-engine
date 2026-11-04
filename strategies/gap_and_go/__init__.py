"""Gap and Go: registration + re-exports."""

from strategies.gap_and_go import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Gap and Go",
        slug="gap_and_go",
        description="Gap-and-Go (momentum day-trading setup), adapted to 1h crypto: a bar gaps >=1.5% from the prior close on >=2x average volume; entry when a bar within the next 3 bars closes beyond the gap bar's extreme in the gap direction; exit when price closes back through the gap bar's midpoint (gap fill).",
        source_name="Gap and Go (momentum day-trading setup)",
        source_url="https://www.luxalgo.com/library/concept/gap-and-go/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
