"""Tom DeMark pivots engine: registration + re-exports."""

from strategies.demark_pivots import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="DeMark Pivots",
        slug="demark_pivots",
        description=(
            "Tom DeMark conditional pivots from the prior 24-bar "
            "'day' OHLC: X = H+2L+C (C<O), 2H+L+C (C>O), H+L+2C "
            "(C=O); R1 = X/2-L, S1 = X/2-H. Long on a close breaking "
            "above R1 and holding 2 bars; short mirrored. Exit on a "
            "close back inside the band or the opposite level "
            "touched; ~1.5xATR stop, ~3xATR target, 24-bar max hold."
        ),
        source_name="DeMark Pivot Points (Tom DeMark)",
        source_url="https://www.babypips.com/learn/forex/other-pivot-point-calculation-methods",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
