"""Chande & Kroll stop engine: registration + re-exports."""

from strategies.chande_kroll import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Chande & Kroll Stop",
        slug="chande_kroll",
        description=(
            "Chande-Kroll trailing stop lines: long_stop = rolling-max(q) of "
            "(highest-high(p) - x*ATR); short_stop = rolling-min(q) of "
            "(lowest-low(p) + x*ATR). Cross of the opposing line = entry "
            "(SMA21 bias), cross of own line = exit — the lines are the "
            "trailing stops. p=10,q=9,x=1.5."
        ),
        source_name="Chande & Kroll, The New Technical Trader (Chande Kroll Stop)",
        source_url="https://www.brokercheck.co.za/how-to-properly-use-the-chande-kroll-stop/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
