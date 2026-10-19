"""Twiggs Money Flow engine: registration + re-exports."""

from strategies.twiggs_money_flow import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Twiggs Money Flow",
        slug="twiggs_money_flow",
        description=(
            "mf_i = v_i*(2*c_i-h_i-l_i)/trange_i with true-range denominator; "
            "TMF = WilderEMA(mf,21)/WilderEMA(v,21); long on cross above 0, "
            "short on cross below 0, exit on cross back through 0; 2xATR stop, "
            "60-bar max hold."
        ),
        source_name="Twiggs Money Flow (mql5 product 451)",
        source_url="https://www.mql5.com/en/market/product/451",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
