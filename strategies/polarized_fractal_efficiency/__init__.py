"""Hans Hannula's Polarized Fractal Efficiency: registration + re-exports."""

from strategies.polarized_fractal_efficiency import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Polarized Fractal Efficiency",
        slug="polarized_fractal_efficiency",
        description="Hannula PFE (N=10, EMA 5): fractal-efficiency ratio of the direct 10-bar distance to the summed single-bar path, signed by the 10-bar move and smoothed. Long on PFE crossing back above 0 after a sub -30 minimum in the last 20 bars, short on the mirror image; exit on the peak-reached reversal past +/-50 or on a cross back through 0.",
        source_name="Hans Hannula — Polarized Fractal Efficiency, TASC January 1994",
        source_url="https://www.investopedia.com/terms/p/pfe.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
