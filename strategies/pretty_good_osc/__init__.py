"""Pretty Good Oscillator engine: registration + re-exports."""

from strategies.pretty_good_osc import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Pretty Good Oscillator",
        slug="pretty_good_osc",
        description=(
            "Mark Johnson's Pretty Good Oscillator: "
            "PGO = (close - SMA(14)) / SMA(ATR(14),14), the close's "
            "distance from its 14-bar mean in average true ranges; "
            "long on a cross above +3.0, short on a cross below -3.0, "
            "exits on a cross back through 0 (close returns to its "
            "SMA); 2xATR stop, 3xATR chandelier trail, 100-bar max hold."
        ),
        source_name="Pretty Good Oscillator (Mark Johnson)",
        source_url="https://lightningchart.com/blog/trader/pretty-good-oscillator/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
