"""Cardwell RSI Ranges: registration + re-exports."""

from strategies.cardwell_rsi_ranges import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Cardwell RSI Ranges",
        slug="cardwell_rsi_ranges",
        description=(
            "Andrew Cardwell range rules on Wilder RSI (14): a bull range holds RSI between 40-80 (20-bar min >= 40), a bear range between 20-60 (20-bar max <= 60). Long on RSI cross above 50 inside a bull range, short on cross below 50 inside a bear range; exits at the range edges (40 / 60)."
        ),
        source_name="Cardwell RSI range rules (Andrew Cardwell)",
        source_url="https://school.stockcharts.com/doku.php?id=technical_indicators:relative_strength_index",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
