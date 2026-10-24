"""Donald Lambert CCI(20) extreme mean reversion: registration + re-exports."""

from strategies.cci_extreme import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="CCI Extreme",
        slug="cci_extreme",
        description=(
            "Donald Lambert's CCI(20) mean reversion on 1h bars. "
            "CCI = (tp - SMA(tp,20)) / (0.015 * mean deviation). "
            "LONG on CCI crossing above -100 from below; SHORT on "
            "CCI crossing below +100 from above. Exit on CCI "
            "crossing 0 in the adverse direction. 2.0xATR stop, "
            "2.5xATR chandelier trail, 96-bar (~4-day) max hold."
        ),
        source_name="Donald Lambert CCI (StockCharts Commodity Channel Index)",
        source_url="https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:commodity_channel_index",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
