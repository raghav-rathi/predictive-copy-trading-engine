"""RSI(2) mean-reversion engine: registration + re-exports."""

from strategies.rsi2 import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="RSI(2) Mean Reversion (Connors)",
        slug="rsi2",
        description=(
            "Connors RSI(2) pullback: SMA200 trend filter, enter on RSI(2) "
            "extremes (<10 long / >90 short), exit on SMA5 cross or RSI unwind; "
            "2xATR stop/target, 48-bar max hold."
        ),
        source_name="Connors & Raschke, Short Term Trading Strategies That Work",
        source_url="https://www.tradingmarkets.com/recent/short_term_trading_strategiesthatwork-connors_raschke-71373.cfm",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
