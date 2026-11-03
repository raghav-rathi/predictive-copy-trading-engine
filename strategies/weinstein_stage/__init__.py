"""Weinstein Stage Analysis: registration + re-exports."""

from strategies.weinstein_stage import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Weinstein Stage Analysis",
        slug="weinstein_stage",
        description=(
            "Stan Weinstein stage analysis on 1h bars (adapted): Stage 2 long when close is above both EMA150 and EMA200 with EMA200 rising over 10 bars; Stage 4 short when close is below both with EMA200 falling. Entries on the first bar of each stage; exits on close crossing back through EMA150."
        ),
        source_name="Weinstein stage analysis (Stan Weinstein)",
        source_url="https://www.investopedia.com/terms/s/stage-analysis.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
