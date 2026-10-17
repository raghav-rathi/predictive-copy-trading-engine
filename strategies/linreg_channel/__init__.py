"""Regression-channel engine: registration + re-exports."""

from strategies.linreg_channel import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Raff linear-regression channel mean-reversion system",
        slug="linreg_channel",
        description=(
            "LSMA(50) +/- 2 sigma of residuals; long the lower-band tag "
            "that closes back inside, short the upper-band tag; exit at "
            "the midline or the opposite band."
        ),
        source_name="Gilbert Raff — linear regression channel",
        source_url="https://www.investopedia.com/terms/r/regression-channel.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
