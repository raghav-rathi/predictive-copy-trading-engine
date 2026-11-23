"""Wilder Parabolic SAR system (raw PSAR, no filters): registration + re-exports."""

from strategies.base import StrategySpec
from strategies.wilder_parabolic_sar import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Wilder Parabolic SAR system",
        slug="wilder_parabolic_sar",
        description=(
            "Wilder Parabolic SAR (1978), raw: LONG while price is "
            "above the SAR, SHORT while below it; the SAR flip "
            "closes one side and opens the other (AF step 0.02, "
            "max 0.20). No MACD or other agreement filter — this "
            "build isolates PSAR's own edge, unlike psar_macd. "
            "2xATR(14) harness stop is a backstop only; 336-bar "
            "max hold; 1% risk, 3x cap."
        ),
        source_name="J. Welles Wilder, New Concepts in Technical Trading Systems (1978)",
        source_url="https://en.wikipedia.org/wiki/Parabolic_SAR",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
