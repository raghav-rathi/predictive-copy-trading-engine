"""Keltner Channel + MACD combo: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.keltner_macd_combo import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Keltner Channel + MACD Combo",
        slug="keltner_macd_combo",
        description=(
            "Keltner Channel (20, 1.5xATR(10)) + MACD(12,26,9): LONG "
            "when the close breaks above the upper Keltner band "
            "(transition only) while the MACD histogram is positive; "
            "SHORT on the mirror break below the lower band while the "
            "histogram is negative. Exit on a close back inside the "
            "channel or the histogram flipping sign. Dual-agreement "
            "filter can agree too late — the known failure mode."
        ),
        source_name="Linda Raschke & Laurence Connors, Street Smarts (1995), Keltner Channel chapter; MACD per Gerald Appel",
        source_url="https://www.tradingview.com/scripts/keltner/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
