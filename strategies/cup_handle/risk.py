"""Cup and Handle risk config.

O'Neil's pattern is a bullish continuation: entries only on the long
side (allow_shorts=False, same convention as darvas_box). The classic
target is the cup-depth projection; here the harness approximates it
with a 4.0xATR target (no trail -- the edge is the breakout leg, not a
managed trend). The 1.5xATR stop sits under the handle low proxy, and
the 120-bar max hold covers the pattern's slow resolution on 1h bars.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=None,
    target_atr_mult=4.0,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    allow_longs=True,
    allow_shorts=False,
)

WARMUP = 320  # 300-bar cup lookback + SMA50 spin-up
