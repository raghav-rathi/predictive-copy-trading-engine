"""MACD + session VWAP: registration + re-exports."""

from strategies.macd_vwap_combo import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="MACD + Session VWAP",
        slug="macd_vwap_combo",
        description="MACD(12, 26, 9) cross entries filtered by the session (UTC-day) VWAP regime: longs only on a bullish MACD cross while close is above the day's VWAP, shorts only on a bearish cross while close is below it; exits on the opposite MACD cross.",
        source_name="MACD (Gerald Appel) + session VWAP",
        source_url="https://www.investopedia.com/terms/m/macd.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
