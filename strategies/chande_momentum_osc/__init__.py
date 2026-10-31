"""Chande Momentum Oscillator: registration + re-exports."""

from strategies.chande_momentum_osc import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Chande Momentum Oscillator",
        slug="chande_momentum_osc",
        description=(
            "Chande Momentum Oscillator threshold strategy: long when "
            "CMO(14) crosses above -50 (leaving oversold), short when it "
            "crosses below +50 (leaving overbought); long exits on a cross "
            "below 0 or above +50, short exits on a cross above 0 or below "
            "-50. 2xATR stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="Chande Momentum Oscillator (Fidelity indicator guide)",
        source_url="https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmo",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
