"""Vortex Indicator crossover engine: registration + re-exports."""

from strategies.vortex import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Vortex Indicator Crossover",
        slug="vortex",
        description=(
            "Vortex Indicator (Botes & Siepman): VM+ = |h - l.shift(1)|, "
            "VM- = |l - h.shift(1)|, VI+(14) = sum14(VM+)/sum14(TR); long "
            "when VI+ crosses above VI-, short on a cross below, exits on "
            "the opposite cross; 2xATR stop, 3xATR chandelier trail, "
            "120-bar max hold."
        ),
        source_name="Vortex Indicator (Botes & Siepman)",
        source_url="https://www.investopedia.com/terms/v/vortex-indicator-vi.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
