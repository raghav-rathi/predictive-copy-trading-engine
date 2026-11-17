"""RSI Volume Confirmation: registration + re-exports."""

from strategies.rsi_volume_confirmation import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="RSI Volume Confirmation",
        slug="rsi_volume_confirmation",
        description="RSI(14) cross of the 50 midline confirmed by volume > 1.25x the trailing 20-bar mean volume: long on a cross above 50 with the volume spike, short on a cross below 50 with the spike; exit on the reverse RSI cross, plus the harness stop/trail.",
        source_name="RSI(14) + volume confirmation (batch-38 spec, no external source supplied)",
        source_url="",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
