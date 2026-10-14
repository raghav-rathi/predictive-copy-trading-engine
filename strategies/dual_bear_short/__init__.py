"""Dual-Bear Pullback Short engine: registration + re-exports."""

from strategies.dual_bear_short import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Dual-Bear Pullback Short (short-only BTC framework)",
        slug="dual_bear_short",
        description=(
            "Short-only: daily EMA21<EMA55 + developing close<EMA55 + daily "
            "volume>=20d SMA gate; entry on two consecutive 4H bear bars "
            "pulling back to within 0.5xATR below 4H EMA21 with 4H volume "
            "confirmation; exit on 4H EMA21 reclaim, 2xATR hard stop."
        ),
        source_name="Dual-Bear Pullback Short — zhangyong78 BTC EMA short research",
        source_url="https://github.com/zhangyong78/qqokx/blob/HEAD/btc_ema_short_research/results_v3_exit_study/research_report.md",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
