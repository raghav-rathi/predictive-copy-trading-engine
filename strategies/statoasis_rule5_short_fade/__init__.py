"""StatOasis Rule 5: Double-Overbought Short Fade — registration + re-exports."""

from strategies.base import StrategySpec
from strategies.statoasis_rule5_short_fade import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="StatOasis Rule 5: Double-Overbought Short Fade",
        slug="statoasis_rule5_short_fade",
        description=(
            "StatOasis Rule 5: SHORT when RSI(14) > 70 AND "
            "Williams %R(14) > -10 AND SMA(100) is falling, with a "
            "fixed 5-bar hold (5h on 1h bars). Long mirror "
            "(RSI < 30, %R < -90, SMA(100) rising) is builder-added. "
            "2xATR stop, no trail/target, 5-bar max hold. "
            "Out-of-sample on SPY daily the rule made +$2,591 at a "
            "75% win rate (Monte Carlo percentile 95.5) but lost "
            "-$720 in-sample — a fade test, not a star."
        ),
        source_name="StatOasis — Can AI Build a Profitable Trading Strategy? 5 Rules Tested",
        source_url="https://statoasis.com/overfit/research/ai-strategy-validation",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
