"""EMA/VWAP breakout-retest engine: registration + re-exports."""

from strategies.ema_vwap_retest import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="EMA/VWAP Breakout-Retest (@EllyDtrades)",
        slug="ema_vwap_retest",
        description=(
            "8/20 EMA + session VWAP trend stack, PDH/PDL breakout memory "
            "(12 bars), entries on 8-EMA pullback or level retest; exits on "
            "8-EMA break; 2xATR disaster stop."
        ),
        source_name="@EllyDtrades 'Copy and Paste Strategy' (X thread, Nov 2024)",
        source_url="https://threadreaderapp.com/thread/1857227985428087014.html",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
