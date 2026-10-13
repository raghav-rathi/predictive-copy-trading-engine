"""Mass Index engine: registration + re-exports."""

from strategies.mass_index import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Mass Index reversal bulge",
        slug="mass_index",
        description=(
            "Dorsey (1992): MI > 27 then < 26.5 reversal bulge; OUR extension "
            "for direction — long if close < SMA(20), short if above; 3xATR "
            "trailing stop."
        ),
        source_name="Donald Dorsey, Stocks & Commodities (June 1992)",
        source_url="https://www.gate.com/crypto-wiki/article/what-is-mass-index-a-comprehensive-guide-to-crypto-reversal-signals-20260116",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
