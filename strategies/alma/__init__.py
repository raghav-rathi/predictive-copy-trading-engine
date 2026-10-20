"""ALMA dual-cross engine: registration + re-exports."""

from strategies.alma import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="ALMA Dual Cross",
        slug="alma",
        description=(
            "Arnaud Legoux moving average (Gaussian weights, sigma=6, "
            "offset=0.85) dual cross: ALMA(9) vs ALMA(21); long on a "
            "cross-up confirmed by a new 20-bar high, short on a "
            "cross-down confirmed by a new 20-bar low; exits on the "
            "opposite cross; 2xATR stop, 3xATR chandelier trail, 200-bar "
            "max hold."
        ),
        source_name="ALMA dual-cross (Hermes strategy, TradingView)",
        source_url="https://cn.tradingview.com/script/nhsUBtUD-Hermes/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
