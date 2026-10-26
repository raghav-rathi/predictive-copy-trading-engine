"""Three White Soldiers / Three Black Crows: registration + re-exports."""

from strategies.three_soldiers_crows import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Three White Soldiers / Three Black Crows",
        slug="three_soldiers_crows",
        description=(
            "Nison three-candle continuation: three same-direction candles with strong bodies, each opening inside the prior body and closing higher (soldiers) or lower (crows)."
        ),
        source_name="Steve Nison, Japanese Candlestick Charting Techniques (Three Advancing White Soldiers / Three Black Crows)",
        source_url="https://epage.pub/doc/6-japanese-candlestick-charting-techniques-by-steve-nison-yvm9x4p2dy",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
