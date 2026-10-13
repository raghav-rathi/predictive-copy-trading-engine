"""TD Sequential engine: registration + re-exports."""

from strategies.td_sequential import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="TD Sequential (DeMark)",
        slug="td_sequential",
        description=(
            "Tom DeMark Sequential: 9-bar setup + 13-bar countdown with "
            "perfection filter and TDST support/resistance exits; 2xATR "
            "disaster stop, 48-bar max hold."
        ),
        source_name="Tom DeMark, The New Science of Technical Analysis (Wiley 1994)",
        source_url="https://www.litefinance.org/blog/for-professionals/technical-analysis-tool-by-tom-demark-td-sequential/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
