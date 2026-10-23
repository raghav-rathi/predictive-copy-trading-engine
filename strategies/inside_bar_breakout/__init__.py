"""Inside bar / mother bar breakout: registration + re-exports."""

from strategies.inside_bar_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Inside Bar Breakout",
        slug="inside_bar_breakout",
        description=(
            "Price-action inside bar breakout (strict: whole range inside "
            "the prior bar). Long when close crosses above the armed "
            "mother-high, short when close crosses below the armed "
            "mother-low; setups expire after 5 bars, a newer inside bar "
            "re-arms the levels, same-bar double-crosses take the mother "
            "bar's direction; opposite breakout exits the position; "
            "1.5xATR stop, 2R target, 48-bar max hold, both directions."
        ),
        source_name="Inside bar candlestick pattern (price-action canon)",
        source_url="https://www.rebelsfunding.com/what-is-the-inside-bar-candlestick-pattern/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
