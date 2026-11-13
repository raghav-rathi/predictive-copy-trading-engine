"""Volume Spread Analysis: registration + re-exports."""

from strategies.volume_spread_analysis import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Volume Spread Analysis",
        slug="volume_spread_analysis",
        description="Tom Williams' Volume Spread Analysis (Master the Markets), building on Wyckoff's law of effort vs result. Long on a no-supply bar (down bar, narrow spread < 0.5x ATR(20), volume lower than each of the previous two bars) or a stopping-volume bar (down bar after a 10-bar decline, volume > 2x the 20-bar mean, close in the upper half of its range); short on a no-demand bar (mirror image) or an upthrust (probe above the 20-bar high closing in the lower third on volume > 1.5x the mean). Exits on the opposite VSA signal, with the harness stop/trail as the exit mechanism.",
        source_name="Tom Williams — Volume Spread Analysis, Master the Markets",
        source_url="https://www.luxalgo.com/library/concept/no-demand-no-supply-bars/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
