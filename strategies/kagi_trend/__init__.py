"""Kagi yang/yin trend engine: registration + re-exports."""

from strategies.kagi_trend import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Kagi Yang/Yin Trend",
        slug="kagi_trend",
        description=(
            "Close-based Kagi chart with a 4xATR(14) reversal amount; line "
            "thickens (yang) when a rising column's high breaks the prior "
            "column's high (shoulder) and thins (yin) when a falling column's "
            "low breaks the prior column's low (waist); long on thin->thick, "
            "short on thick->thin, exits on the opposite transition; "
            "2xATR stop, 100-bar max hold."
        ),
        source_name="Kagi chart technique (marketinout.com)",
        source_url="https://www.marketinout.com/technical_analysis.php?t=Kagi&id=56",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
