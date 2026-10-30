"""Money Flow Index: registration + re-exports."""

from strategies.money_flow_index import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Money Flow Index",
        slug="money_flow_index",
        description=(
            "Volume-weighted RSI: MFI(14) crosses back above 20 "
            "from below for longs, back below 80 from above for "
            "shorts, exit on a 50-midline cross against the "
            "position. 2xATR stop, 2.5xATR trail, 120-bar max hold."
        ),
        source_name="Money Flow Index (MFI), StockCharts ChartSchool (Gene Quong and Avrum Soudack)",
        source_url="https://school.stockcharts.com/doku.php?id=technical_indicators:money_flow_index_mfi",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
