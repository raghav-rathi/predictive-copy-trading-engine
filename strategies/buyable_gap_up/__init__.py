"""Morales & Kacher Buyable Gap-Up (BGU): registration + re-exports."""

from strategies.base import StrategySpec
from strategies.buyable_gap_up import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Morales & Kacher Buyable Gap-Up (BGU)",
        slug="buyable_gap_up",
        description=(
            "Morales & Kacher Buyable Gap-Up: LONG when the open "
            "gaps >= 0.75xATR(40) above the prior close on volume "
            ">= 1.5x the 1200-bar (50-day) average, in an uptrend "
            "(price above SMA50 and SMA200). Stop is the gap bar's "
            "intraday low (signal-level exit); also exits on a "
            "close below the 240-bar SMA (10-day equivalent). "
            "Crypto trades 24/7 so there is no true overnight gap — "
            "the 1h open-vs-prior-close gap is the adaptation and "
            "will be much smaller/rarer than in equities. Short "
            "mirror is builder-added."
        ),
        source_name="MaxMarkets — Morales and Kacher Buyable Gap-Up (Morales & Kacher, In the Buy Zone)",
        source_url="https://maxmarkets.app/learn/strategies/morales_kacher_bgu",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
