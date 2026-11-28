"""Balance Line pullback engine: registration + re-exports."""

from strategies.base import StrategySpec
from strategies.registry import register
from strategies.balance_line_pullback import indicators, risk, signals

SPEC = register(
    StrategySpec(
        name="Balance Line Pullback (Bill Williams)",
        slug="balance_line_pullback",
        description=(
            "Bill Williams Balance Line trade: price pulls back "
            "to touch the Alligator Jaw -- SMMA(13) of median "
            "price -- then turns with the mouth open (lips > "
            "teeth > jaw for longs, mirrored for shorts). "
            "Exit on a close back through the jaw, the lips "
            "crossing the teeth (mouth closing), or the "
            "opposite entry; 2xATR stop, 3xATR trail, 96-bar "
            "max hold."
        ),
        source_name="Balance Line trades — Bill Williams, Trading Chaos / New Trading Dimensions",
        source_url="https://www.forexfactory.com/thread/26044-profitunity-chaos-trading-system-by-bill-williams?page=83",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
