"""Kairi Relative Index: registration + re-exports."""

from strategies.kairi_index import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Kairi Relative Index",
        slug="kairi_index",
        description=(
            "Kairi Relative Index (25): (close - SMA25) / SMA25 x 100. Mean reversion: long on recovery cross above -5 after an oversold dip, short on breakdown cross below +5 after an overbought peak; exits at the mean (0)."
        ),
        source_name="Kairi Relative Index",
        source_url="https://www.investopedia.com/terms/k/kairi-relative-index-kri.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
