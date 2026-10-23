"""Rolling session-less VWAP cross: registration + re-exports."""

from strategies.vwap_cross import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Rolling VWAP Cross",
        slug="vwap_cross",
        description=(
            "24-bar rolling VWAP cross on 1h crypto bars (crypto trades "
            "24/7, so no session anchor). LONG when close crosses above "
            "the rising 24-bar VWAP on 1.2x average volume; SHORT on the "
            "mirror. Exit on the opposite cross. 1.5xATR stop, 2xATR "
            "chandelier trail, 72-bar (~3-day) max hold."
        ),
        source_name="VWAP cross (algotradinglib / BingX VWAP guide)",
        source_url="https://algotradinglib.com/en/pedia/v/vwap_cross.html",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
