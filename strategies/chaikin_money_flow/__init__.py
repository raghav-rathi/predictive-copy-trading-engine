"""Chaikin Money Flow zero-cross: registration + re-exports."""

from strategies.chaikin_money_flow import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Chaikin Money Flow Zero-Cross",
        slug="chaikin_money_flow",
        description=(
            "Volume-weighted accumulation/distribution oscillator: "
            "CMF(20) = sum of money flow volume over 20 bars divided "
            "by sum of volume over 20 bars. Long on a cross above the "
            "zero line, short on a cross below it, exit on the "
            "opposite cross. 2xATR stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="Chaikin Money Flow (CMF) — Fidelity technical indicator guide",
        source_url="https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmf",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
