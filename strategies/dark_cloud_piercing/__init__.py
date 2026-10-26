"""Dark Cloud Cover / Piercing Line: registration + re-exports."""

from strategies.dark_cloud_piercing import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Dark Cloud Cover / Piercing Line",
        slug="dark_cloud_piercing",
        description=(
            "Nison two-candle reversal pair: dark cloud (white then black closing below the midpoint) and piercing line (black then white closing above the midpoint)."
        ),
        source_name="Steve Nison, Japanese Candlestick Charting Techniques (Dark-Cloud Cover / Piercing Pattern)",
        source_url="https://epage.pub/doc/6-japanese-candlestick-charting-techniques-by-steve-nison-yvm9x4p2dy",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
