"""SMI Ergodic Oscillator crossover: registration + re-exports."""

from strategies.smi_ergodic import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="SMI Ergodic Oscillator Crossover",
        slug="smi_ergodic",
        description=(
            "William Blau's SMI Ergodic Oscillator ('Momentum, Direction, "
            "and Divergence', 1995): smi = 100 * EMA(EMA(m, 5), 20) / "
            "EMA(EMA(|m|, 5), 20), signal = EMA(smi, 5), zones at +/-40. "
            "LONG when smi crosses above its signal from at/below -40 "
            "(oversold); SHORT when it crosses below from at/above +40 "
            "(overbought); exit on the opposite cross. 1.5xATR stop, "
            "2xATR chandelier trail, 96-bar max hold."
        ),
        source_name="William Blau, SMI Ergodic Oscillator ('Momentum, Direction, and Divergence', 1995)",
        source_url="https://en.wikipedia.org/wiki/True_strength_index",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
