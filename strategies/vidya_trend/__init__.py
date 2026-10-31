"""VIDYA trend: registration + re-exports."""

from strategies.vidya_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="VIDYA Trend",
        slug="vidya_trend",
        description=(
            "Tushar Chande Variable Index Dynamic Average: an EMA "
            "whose smoothing factor scales with |CMO(9)|, so it "
            "tracks fast in strong trends and flattens in chop. Long "
            "on a close cross above VIDYA, short on a cross below, "
            "exit on the opposite cross. 2xATR stop, 2.5xATR trail, "
            "120-bar max hold."
        ),
        source_name="Tushar Chande VIDYA (MetaTrader 5 indicator reference)",
        source_url="https://www.metatrader5.com/en/terminal/help/indicators/trend_indicators/vida",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
