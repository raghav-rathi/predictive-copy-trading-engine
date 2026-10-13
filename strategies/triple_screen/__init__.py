"""Triple Screen engine: registration + re-exports."""

from strategies.triple_screen import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Elder Triple Screen (4h MACD tide / 1h FI2 wave / stop trigger)",
        slug="triple_screen",
        description=(
            "4h MACD histogram slope sets the tide; 1h FI2 zero-cross against "
            "the tide arms the wave; prior-bar high/low breakout triggers the "
            "entry; 2xATR(14) protective stop; exit on tide flip or FI2 hook."
        ),
        source_name="Alexander Elder, Trading for a Living (Wiley, 1993)",
        source_url="https://github.com/fscheu/quantagent/blob/HEAD/docs/03_design/QuantAgent-vna-DS-triple-screen-strategy.md",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
