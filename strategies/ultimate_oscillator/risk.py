"""Ultimate Oscillator divergence risk config.

Divergence setups are swing trades: the trigger (UO crossing the
divergence high/low) already demands momentum confirmation, so a
1.5xATR hard stop with a 2xATR chandelier trail fits the structure.
No fixed target -- exits are signal-driven (UO crossing 70/30).
96-bar (~4 day) max hold keeps a failed divergence from tying up
capital. Both directions allowed: Williams' method is symmetric.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=2.0,
    target_atr_mult=None,
    max_hold_bars=96,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 80  # UO(28) spin-up + pivot-confirmation margin
