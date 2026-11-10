"""David Weis's Weis Wave: registration + re-exports."""

from strategies.weis_wave import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Weis Wave",
        slug="weis_wave",
        description="David Weis's Weis Wave: volume grouped by price swing instead of per bar. A swing ends when the close reverses 1.5x ATR(14) from the running swing extreme. Long on a new up-wave starting after a down-wave whose volume was under 85% of the up-wave before it (selling effort drying up); short on the mirror. Exit when the wave flips the other way.",
        source_name="David Weis — Trades About to Happen (Weis Wave)",
        source_url="https://forexcalculator.pro/weis-wave-volume-indicator-mt5/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
