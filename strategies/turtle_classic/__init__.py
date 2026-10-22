"""Original Turtle Rules engine: registration + re-exports."""

from strategies.turtle_classic import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Original Turtle Rules",
        slug="turtle_classic",
        description=(
            "Original Turtle Trading Rules (Dennis/Eckhardt via Curtis "
            "Faith): System 1 takes 20-bar Donchian breakouts, skipped "
            "when the previous System-1 trade in the same direction was "
            "a winner; System 2 takes 55-bar breakouts as a failsafe; "
            "exits on the 10-bar (S1) / 20-bar (S2) opposite-channel "
            "cross; 2xATR(20) stop; 1% risk per trade; 3x leverage. No "
            "pyramiding -- single unit per position. Adapted from daily "
            "to 1h bars."
        ),
        source_name="Original Turtle Trading Rules (Curtis Faith, 2003)",
        source_url="http://mql5.com/en/articles/23448",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
