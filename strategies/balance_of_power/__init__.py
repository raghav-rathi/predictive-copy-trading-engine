"""Balance of Power control-shift engine: registration + re-exports."""

from strategies.balance_of_power import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Balance of Power",
        slug="balance_of_power",
        description=(
            "Balance of Power (Igor Livshin, S&C Aug 2001): "
            "raw_bop = (close - open) / (high - low), bop = SMA(raw, 14); "
            "long when bop crosses above zero (buyers take control), "
            "short when it crosses below zero; exits on the opposite "
            "zero-cross; 2xATR stop, 2.5xATR trail, 150-bar max hold."
        ),
        source_name="Balance of Power (Igor Livshin, S&C Aug 2001)",
        source_url=(
            "https://chartschool.stockcharts.com/table-of-contents/"
            "technical-indicators-and-overlays/technical-indicators/"
            "balance-of-power-bop.md"
        ),
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
