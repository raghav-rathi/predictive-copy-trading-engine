"""Vortex + ADX: registration + re-exports."""

from strategies.vortex_adx import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Vortex + ADX",
        slug="vortex_adx",
        description="Botes & Siepman's Vortex indicator (TASC, Jan 2010) with an ADX filter: VI+ = EMA(14) of |high - prev low| / EMA(14) of true range, VI- the mirror. Long on a VI+ cross above VI- with ADX(14) > 25, short on the mirror cross; exit on the opposite VI cross or ADX(14) < 20, with the harness stop/trail as the exit mechanism.",
        source_name="Etienne Botes & Douglas Siepman — The Vortex Indicator, Technical Analysis of Stocks & Commodities (Jan 2010)",
        source_url="https://capital.com/en-eu/learn/technical-analysis/vortex-indicator",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
