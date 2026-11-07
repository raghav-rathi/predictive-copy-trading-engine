"""Andrews Pitchfork: registration + re-exports."""

from strategies.andrews_pitchfork import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Andrews Pitchfork",
        slug="andrews_pitchfork",
        description="Andrews Pitchfork median-line system (Dr. Alan Andrews) on 5-bar fractal pivots: the most recent alternating pivot triple P0/P1/P2 (P2 beyond P0) defines a fork whose median line runs from P0 through the midpoint of P1-P2, with parallels through P1 and P2; enter long on a bounce off the lower parallel (low within 0.25x ATR(14), close back above it), target the median line, exit on a close outside the fork; short mirror off the upper parallel.",
        source_name="Andrews Pitchfork median-line system (FX Foundations)",
        source_url="https://www.fxfoundations.com/learn/technical-analysis/median-line-pitchfork",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
