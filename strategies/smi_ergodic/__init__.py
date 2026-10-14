"""SMI Ergodic engine: registration + re-exports."""

from strategies.smi_ergodic import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Blau SMI Ergodic signal-line system",
        slug="smi_ergodic",
        description=(
            "SMI = 100*doubleEMA(d)/doubleEMA(|d|); long when it crosses "
            "above its 5-bar signal while positive, short on the mirror "
            "while negative; exit on the opposite cross."
        ),
        source_name="William Blau — SMI Ergodic (Momentum, Direction, and Divergence, 1995)",
        source_url="https://www.luxalgo.com/blog/smi-ergodic-oscillator-smi-indicator-vs-oscillator/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
