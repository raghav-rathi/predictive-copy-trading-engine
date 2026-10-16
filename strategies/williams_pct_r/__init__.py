"""Williams %R engine: registration + re-exports."""

from strategies.williams_pct_r import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Larry Williams %R reversal trigger",
        slug="williams_pct_r",
        description=(
            "%R hits -100 (0), waits 5 bars, reverses through -85 (-15); "
            "exits at the opposite extreme zone; 2xATR stop, 48-bar hold."
        ),
        source_name="Larry Williams %R (How I Made One Million Dollars Last Year Trading Commodities, 1979)",
        source_url="https://en.wikipedia.org/wiki/Williams_%25R",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
