"""Fractal Dimension Index: registration + re-exports."""

from strategies.fractal_dimension_index import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Fractal Dimension Index",
        slug="fractal_dimension_index",
        description="Ehlers Fractal Dimension Index over 30 bars: FDI = (ln(sum of |close-to-close changes|) - ln(highest high - lowest low)) / ln(2), clipped to [1, 2]. Readings below 1.4 mark a clean trend, above 1.5 a ranging/choppy market. Long when FDI < 1.4 and close crosses above SMA(20); short when FDI < 1.4 and close crosses below SMA(20); exit when FDI rises above 1.5 or the close crosses back through SMA(20).",
        source_name="Fractal Dimension Index (Ehlers)",
        source_url="https://docs.prorealalgos.com/fractaldimensionindex.html",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
