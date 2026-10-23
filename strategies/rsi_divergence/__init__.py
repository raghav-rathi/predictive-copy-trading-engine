"""Classical RSI divergence engine: registration + re-exports."""

from strategies.rsi_divergence import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="RSI regular divergence (Wilder)",
        slug="rsi_divergence",
        description=(
            "Wilder RSI(14) with 5-bar fractal pivots on price and RSI; "
            "regular bullish/bearish divergences confirmed by an RSI "
            "30/70 re-cross within 20 bars; 1.5xATR stop, 2.5xATR trail, "
            "72-bar max hold. Hidden divergence is a listed extension, "
            "not implemented."
        ),
        source_name="RSI divergence (classical, Wilder lineage)",
        source_url="https://github.com/iamsengio/agent-trading-skills/blob/HEAD/skills/technical-strategies/rsi-divergence/SKILL.md",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
