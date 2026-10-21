"""Elder Triple Screen engine: registration + re-exports."""
from strategies.elder_triple_screen import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Elder Triple Screen",
        slug="elder_triple_screen",
        description=(
            "Alexander Elder's Triple Screen: 6h MACD-histogram trend screen "
            "(the tide), 1h Force Index EMA(2) wave for pullback entries, "
            "exit when the trend screen flips."
        ),
        source_name="Triple Screen (Alexander Elder, Trading for a Living)",
        source_url="https://tradingwriters.substack.com/p/elders-triple-screen-trading-system",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
