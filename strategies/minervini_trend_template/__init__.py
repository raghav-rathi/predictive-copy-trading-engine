"""Minervini Trend Template (SEPA gate): registration + re-exports."""

from strategies.base import StrategySpec
from strategies.minervini_trend_template import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Minervini Trend Template (SEPA gate)",
        slug="minervini_trend_template",
        description=(
            "Mark Minervini's 8-condition Trend Template (SEPA) gate "
            "on 1h bars: price above SMA150/200, SMA150 above SMA200, "
            "SMA200 rising over ~1 month (720 bars), SMA50 above "
            "both, price above SMA50, >=25% above the trailing low, "
            "within 25% of the trailing high, RSI(14) > 55 as the "
            "Relative Strength proxy. Entry on a close above the "
            "trailing 20-bar high while the gate holds; exit on a "
            "close below SMA50. ~7.5% stop approximated as 6xATR, "
            "8xATR trail, 720-bar max hold. Short mirror is "
            "builder-added."
        ),
        source_name="MQL5 — Automating Classic Market Methods (Part 4): Mark Minervini's Trend Template",
        source_url="http://mql5.com/en/articles/22790",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
