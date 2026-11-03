"""Wyckoff Sign of Strength: registration + re-exports."""

from strategies.wyckoff_sos import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Wyckoff Sign of Strength",
        slug="wyckoff_sos",
        description=(
            "Wyckoff sign of strength / weakness: a close above the prior 40-bar high on volume over 1.5x its 20-bar average is a sign of strength (long); a close below the prior 40-bar low on the same volume condition is a sign of weakness (short). Exits on close back inside the range."
        ),
        source_name="Wyckoff sign of strength (Richard Wyckoff)",
        source_url="https://school.stockcharts.com/doku.php?id=chart_school:market_analysis:wyckoff_method",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
