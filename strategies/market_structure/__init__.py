"""Market-structure engine: registration + re-exports."""

from strategies.market_structure import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="SMC market-structure (BOS/CHoCH) trend system",
        slug="market_structure",
        description=(
            "Fractal (2,2) swing pivots; bullish/bearish break-of-structure "
            "continues the leg, change-of-character reverses it; exit when "
            "structure breaks the other way."
        ),
        source_name="SMC — BOS/CHoCH structure mechanics (LuxAlgo/TV docs)",
        source_url="https://www.tradingview.com/scripts/liquiditysweep/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
