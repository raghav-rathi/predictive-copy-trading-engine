"""Asia Sweep engine: registration + re-exports."""

from strategies.asia_sweep import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Asia Session Liquidation Sweep",
        slug="asia_sweep",
        description=(
            "Fade prior-session liquidity sweeps: London (07-10 UTC) and NY "
            "(12-15 UTC, ex 14:00) entries on sweep-and-reclaim of the Asia / "
            "London extreme with persistent 30-bar BOS bias, 0.10xATR min "
            "sweep depth, 1xATR stop / 3R target, flat at 20:00 UTC."
        ),
        source_name="Asia Sweep EA spec — grahamovernightly/edgefindr",
        source_url="https://github.com/grahamovernightly/edgefindr/blob/HEAD/ea/Asia_Sweep_EA_spec.md",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
