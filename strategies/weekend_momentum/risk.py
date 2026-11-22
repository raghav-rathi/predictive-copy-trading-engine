"""Weekend crypto momentum risk config.

A weekend session is 72 hourly bars (Fri 00:00 – Sun 23:59 UTC),
so the 72-bar max hold is the backstop for the Monday-open signal
exit. The stop is a roomy 2xATR with a 2xATR chandelier trail —
weekend moves can be sharp, and the trail lets a weekend trend run
while the Monday exit does the time management. No fixed target:
the thesis is "hold the weekend momentum", not a price level.
Long/short symmetric.
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

WARMUP = 192  # 168-bar momentum lag + one day of margin
