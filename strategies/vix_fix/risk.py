"""VIX Fix risk config.

Fear spikes are mean-reversion plays: the edge decays fast once the
spike deflates, so the midline exit plus a tight 24-bar max hold do
the trade management. No trailing and no fixed target -- the setup is
"fear spike -> relief bounce", not a trend runner. A hard 2xATR stop
covers a genuine breakdown where the fear was justified.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=24,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # WVF(22) + Bollinger(20) spin-up
