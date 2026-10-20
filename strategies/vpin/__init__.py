"""VPIN Toxicity Exhaustion: registration + re-exports."""

from strategies.vpin import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="VPIN Toxicity Exhaustion",
        slug="vpin",
        description=(
            "Bulk Volume Classification per 1h bar feeds volume buckets "
            "(bucket size = trailing 50-bar mean volume, remainder "
            "carried); VPIN = mean |buy-sell|/bucket over the last 50 "
            "buckets, ranked as a percentile over 252 bars. Long when "
            "VPIN percentile > 0.90 AND the close makes a new 20-bar low "
            "(panic exhaustion); short symmetric on new 20-bar highs. "
            "No signal exits — 2xATR stop, 2xATR target, 48-bar max hold "
            "manage the trade."
        ),
        source_name="VPIN (Easley/de Prado/O'Hara via jheusser.github.io; QuantEdge TradingView)",
        source_url="https://jheusser.github.io/2013/10/13/informed-trading.html",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
