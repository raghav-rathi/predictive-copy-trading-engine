"""Williams breakout engine: registration + re-exports."""

from strategies.williams_breakout import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Williams Volatility Breakout",
        slug="williams_breakout",
        description=(
            "24h high/low breakouts gated by range expansion (>1.5x 20-bar "
            "avg range); 1.5xATR stop, 2xATR target, 48-bar cap."
        ),
        source_name="Larry Williams volatility breakout (public)",
        source_url="https://www.investopedia.com/articles/trading/02/081402.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
