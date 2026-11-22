"""ClucHAnix (Freqtrade, crypto-native): registration + re-exports."""

from strategies.base import StrategySpec
from strategies.cluchanix import indicators, risk, signals
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="ClucHAnix (Freqtrade, crypto-native)",
        slug="cluchanix",
        description=(
            "Freqtrade ClucHAnix ported to 1h bars with the published "
            "hyperopt constants: Heikin Ashi + Bollinger Bands (40, 2s) "
            "pullback to the lower band with BBDelta/close-delta/tail "
            "filters, gated by ROCR(168) on 1h closes; exit on Fisher "
            "> 0.38414 with two lower HA highs and price above the BB "
            "mid. Short side is a builder-added mirror of the "
            "long-only source. 6xATR stop/trail, 72-bar max hold."
        ),
        source_name="ssssi/freqtrade_strs — ClucHAnix",
        source_url="https://deepwiki.com/ssssi/freqtrade_strs/5.2-cluchanix-strategy",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
