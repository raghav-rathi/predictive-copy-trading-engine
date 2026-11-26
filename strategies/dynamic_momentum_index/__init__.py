"""Dynamic Momentum Index engine: registration + re-exports."""

from strategies.dynamic_momentum_index import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Dynamic Momentum Index",
        slug="dynamic_momentum_index",
        description=(
            "Chande & Kroll Dynamic Momentum Index: a variable-"
            "lookback RSI whose window TD = clamp(int(14/Vi), 5, "
            "30) shortens in volatility and lengthens in calm; "
            "long on a cross up through 30, short on a cross down "
            "through 70, exit on a cross back through 50; 2xATR "
            "stop, 3xATR trail, 120-bar max hold."
        ),
        source_name="Tushar Chande & Stanley Kroll — The New Technical Trader (1994); S&C V.11:5",
        source_url="https://www.luxalgo.com/library/concept/dynamic-momentum-index/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
