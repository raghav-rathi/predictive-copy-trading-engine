"""VWAP session breakout: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.registry import register
from strategies.vwap_session_breakout import indicators, risk, signals

SPEC = register(
    StrategySpec(
        name="VWAP Session Breakout",
        slug="vwap_session_breakout",
        description=(
            "UTC-day session VWAP breakout: LONG when the close "
            "breaks above VWAP + 1.0 volume-weighted SD with "
            "above-average session volume; SHORT on the mirror. "
            "Exit on a close back through VWAP; 24-bar (one "
            "session) max hold. Same session-VWAP construction "
            "as vwap_bollinger_bands but WITHOUT its ADX filter — "
            "the raw breakout, unfiltered. 24/7 crypto has no "
            "true session open, so the UTC-midnight anchor is an "
            "adaptation."
        ),
        source_name="Brian Shannon, Technical Analysis Using Multiple Timeframes (2008), VWAP chapter",
        source_url="https://www.alphatrends.net/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
