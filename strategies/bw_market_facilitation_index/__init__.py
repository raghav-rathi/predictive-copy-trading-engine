"""Bill Williams Market Facilitation Index squat breakout: registration + re-exports."""

from strategies.bw_market_facilitation_index import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Bill Williams Market Facilitation Index Squat Breakout",
        slug="bw_market_facilitation_index",
        description="Bill Williams' MFI (range / volume) classifies each bar GREEN/FADE/FAKE/SQUAT vs the previous bar. A SQUAT (MFI down, volume up) marks a battle; a close beyond the squat bar's high/low within 5 bars, confirmed by EMA(20), enters long/short. Exit on a FADE bar or an EMA(20) cross.",
        source_name="Bill Williams — Trading Chaos (BW MFI)",
        source_url="https://www.luxalgo.com/library/concept/bill-williams-market-facilitation-index/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
