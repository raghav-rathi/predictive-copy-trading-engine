"""DPO zero-line cross risk config.

DPO cycles are mid-frequency turns (a 20-bar oscillator on 1h data
marks roughly day-long cycles): positions need room for the cycle to
play out, so the max hold is 150 bars (~6 days) and the 2.5xATR
chandelier trail banks extended legs while the 2xATR hard stop caps
the failure case -- a cycle cross that reverses usually dies fast. No
fixed target -- exits are cross-driven. 1% risk/trade, 3x leverage.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=2.5,
    target_atr_mult=None,
    max_hold_bars=150,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 80  # SMA(50) spin-up (50 bars) + DPO(20) displaced lag, with margin
