"""RSI + MACD confluence: registration + re-exports."""

from strategies.rsi_macd_combo import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="RSI + MACD Confluence",
        slug="rsi_macd_combo",
        description="Long when RSI(14) crosses above 50 with MACD histogram > 0; short when RSI crosses below 50 with histogram < 0; exit on the RSI recross against the position. 2xATR stop, 2.5xATR trail, 168-bar max hold.",
        source_name="RSI + MACD confluence (J. Welles Wilder; Gerald Appel)",
        source_url="https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/relative-strength-index-rsi",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
