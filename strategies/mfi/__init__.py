"""Money Flow Index engine: registration + re-exports."""

from strategies.mfi import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Money Flow Index (Quong & Soudack, 1989)",
        slug="mfi",
        description=(
            "Volume-weighted RSI: long on MFI(14) crossing above 20 from "
            "oversold, short on crossing below 80 from overbought, exit at "
            "the opposite extreme."
        ),
        source_name="Money Flow Index (Gene Quong & Avrum Soudack, 1989) — Investopedia",
        source_url="https://www.investopedia.com/terms/m/mfi.asp",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
