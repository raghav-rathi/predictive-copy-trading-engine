"""UT Bot Alerts engine: registration + re-exports."""

from strategies.ut_bot import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="UT Bot Alerts",
        slug="ut_bot",
        description=(
            "QuantNomad's UT Bot Alerts (original idea HPotter): ATR(10) "
            "trailing stop with KeyValue 1.0; long when close crosses "
            "above the stop, short when it crosses below, exit on the "
            "opposite flip; 2xATR stop, 3xATR trail, 60-bar max hold."
        ),
        source_name='QuantNomad, "UT Bot Alerts" (TradingView)',
        source_url="https://proea.app/en/blog/ut-bot-alerts-settings",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
