"""Outside-bar reversal: registration + re-exports."""

from strategies.outside_bar_reversal import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Outside-Bar Reversal",
        slug="outside_bar_reversal",
        description="Outside-bar reversal at swing extremes: an outside bar (high above and low below the previous bar) after a close below/above SMA(20), closing in the upper/lower third of its range with volume above its 20-bar average, enters long/short; exit on an opposing outside bar or a close below/above the entry outside bar's low/high.",
        source_name="LuxAlgo — Outside Bar",
        source_url="https://www.luxalgo.com/library/concept/outside-bar/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
