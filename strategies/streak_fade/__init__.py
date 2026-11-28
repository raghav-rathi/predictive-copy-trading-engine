"""Consecutive up/down days fade engine: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.registry import register
from strategies.streak_fade import indicators, risk, signals

SPEC = register(
    StrategySpec(
        name="Consecutive Days Fade (Connors)",
        slug="streak_fade",
        description=(
            "Larry Connors consecutive up/down days: fade a 4th "
            "consecutive up close (short) or a 4th consecutive "
            "down close (long), betting the streak mean-reverts. "
            "Exit on a close crossing back through SMA(10) or "
            "the opposite entry; 2xATR stop, 3xATR trail, "
            "24-bar max hold."
        ),
        source_name="Consecutive up/down days — Larry Connors, TradingMarkets 2007",
        source_url="https://tradingmarkets.com/recent/if_a_stock_drops_5_days_in_a_row_should_you_buy_it-674228",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
