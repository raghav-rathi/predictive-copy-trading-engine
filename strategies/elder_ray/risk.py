"""Elder Ray risk config.

Elder Ray trades are swing-style: hold the dip-to-exhaustion leg, so no
fixed take-profit (exits are signal-driven: bear_power exhaustion or
trend-slope loss). 1.5xATR hard stop -- the dip must prove itself quickly;
2xATR chandelier trail to lock in the leg once bull_power runs. 120-bar
(~5 day on 1h) max hold keeps a dead position from tying up capital.
Both sides live (the strategy is a true mirror). 1% risk/trade, 3x
leverage cap, Hyperliquid taker fees + slippage.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=2.0,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 60  # EMA(13) + power spin-up, with margin
