"""Schiff Pitchfork: registration + re-exports."""

from strategies.schiff_pitchfork import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Schiff Pitchfork Median-Line Pullback",
        slug="schiff_pitchfork",
        description="Schiff pitchfork median-line pullback: three consecutive confirmed 10-bar pivots (low-high-low or high-low-high) anchor a Schiff fork whose median line starts at (A bar, (A+B)/2) and runs through the B-C midpoint, with parallels through B and C; long on a touch of the bullish median line from above (low within 0.5 ATR(14)) followed by a close back above it, short on the mirror; exit on the opposite signal or a close beyond the far parallel, plus the harness stop/trail. Distinct from andrews_pitchfork, which anchors the median line at A itself.",
        source_name="Schiff pitchfork / median-line (FX Foundations)",
        source_url="https://www.fxfoundations.com/learn/technical-analysis/median-line-pitchfork",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
