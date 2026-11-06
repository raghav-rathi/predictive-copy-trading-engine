"""Rounding Bottom: registration + re-exports."""

from strategies.rounding_bottom import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Rounding Bottom",
        slug="rounding_bottom",
        description="Rounding bottom / saucer (Edwards & Magee): a 60-bar U-shape with the trough in the middle third, rims within 2%, trough >= 3x ATR below the rims, SMA slope down then up; long on a close above the neckline with volume confirmation. Rounding-top mirror trades the short side.",
        source_name="Rounding Bottom / Saucer (Edwards & Magee)",
        source_url="https://www.indiainfoline.com/knowledge-center/online-share-trading/what-is-the-rounding-bottom-patterns",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
