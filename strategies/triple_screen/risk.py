"""Triple Screen risk: Elder's protective stop sits below the entry bar's low
(above its high for shorts), i.e. roughly one bar's range away. A 2xATR(14)
hard stop reproduces that scale without bar-relative bookkeeping. No
trailing (the wave exit manages winners), no fixed target; tide flips can
be slow, so the max hold is generous at 336 bars (2 weeks)."""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=336,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=True,
)

# MACD(26,9) on 4h + closed-bar shift + FI/ATR warmup: 168 1h bars.
WARMUP = 168
