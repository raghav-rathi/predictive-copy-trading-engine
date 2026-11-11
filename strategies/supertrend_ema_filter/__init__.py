"""Supertrend + EMA(200) filter: registration + re-exports."""

from strategies.supertrend_ema_filter import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Supertrend + EMA(200) Filter",
        slug="supertrend_ema_filter",
        description="Supertrend(10, 3.0) flips for entries/exits, filtered by an EMA(200) regime line: longs only when close is above EMA(200), shorts only when close is below it. A deliberately filtered variant of the existing supertrend strategy (precedent: supertrend_adx_filter).",
        source_name="Olivier Seban Supertrend + EMA regime filter",
        source_url="https://www.updata.co.uk/developers/docs/libmanstrat/supertrend",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
