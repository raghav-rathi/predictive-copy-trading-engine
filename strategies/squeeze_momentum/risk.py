"""LazyBear Squeeze Momentum risk config.

Source mechanics: the TradingView strategy sizes positions at
8% of equity and relies on the momentum-reversal signal exit
(first downtick of the histogram for longs); it recommends a
stop-loss but does not specify one.

DEVIATION (documented, see CALIBRATION.md): the harness sizes
by 1% equity risk on the stop distance (house standard), not
by 8% of equity, and a 2xATR(14) hard stop is ADDED as a
backstop — the source has no specified stop. No trail, no
target. Max hold 120 bars (~5 days): a squeeze-release move
that has not run in five days is not the trade, and the
first-downtick exit normally fires far sooner.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=2.0,
    trail_atr_mult=None,
    target_atr_mult=None,
    max_hold_bars=120,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 110  # 100-bar momentum extreme + margin
