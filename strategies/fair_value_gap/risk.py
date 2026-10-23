"""Fair Value Gap risk config.

ICT gap-retest trades are mean-reversion-into-continuation plays: price
dips into the imbalance and rejects, so the trade is invalidated fast
when the dip keeps going. The ICT rule is "stop beyond the far edge"
(fvg_low for longs), which the harness approximates with a wide
2.0xATR hard stop rather than a zone-relative stop -- honest about the
gap between the rule and the implementation. The 2.0xATR chandelier
trail lets a retest winner run once momentum confirms, and the
72-bar (~3 day) max hold keeps a stalled retest from tying up capital.
Both directions allowed: bullish and bearish gaps are symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.0,
    target_atr_mult=None,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 80  # ATR(14) + FVG detection spin-up, with margin
