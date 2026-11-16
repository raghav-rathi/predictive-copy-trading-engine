"""McClellan Oscillator risk config.

Breadth extremes are mean-reverting on 1h bars: the oscillator
whipsaws through 0 far more often than a genuine breadth thrust
develops, so positions get a tight 1.5xATR stop, a 2.5xATR target
and a short 48-bar max hold (~2 days). No trailing stop — exits are
oscillator-driven (cross back through 0 or the summation index
turning against the position), and the hard stop/target bound the
failure case. The 48-bar cap keeps stale breadth trades from
lingering through the next regime.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=None,
    target_atr_mult=2.5,
    max_hold_bars=48,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # EMA39 spin-up (39 bars) + RANA window (24) + margin
