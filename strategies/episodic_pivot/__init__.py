"""Episodic Pivot: registration + re-exports."""

from strategies.episodic_pivot import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Episodic Pivot",
        slug="episodic_pivot",
        description="Episodic Pivot (Pradeep Bonde / Qullamaggie), adapted from daily equities to 1h crypto: after a dull base (ATR at/below its 50-bar median), a bar gaps >=2% above the prior close on >=3x average volume and closes above the prior 20-bar high. Long only; the gap bar's continuation is the trade, exit on a close back below SMA(20).",
        source_name="Episodic Pivot (Pradeep Bonde / Qullamaggie)",
        source_url="https://www.kristjankullamagi.com/setups/episodic-pivot/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
