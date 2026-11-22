"""BTC Breakout Trend Climber risk config.

Source mechanics (QuantConnect backtest): initial stop at entry
minus 3.5xATR(5); once price rises 1xATR(15) above entry, trail
11xATR(10) below the last price; exit on a close below the stop.

DEVIATION (documented, see CALIBRATION.md): the harness's
RiskConfig carries a single ATR window, so the three source ATR
windows (5 / 15 / 10) cannot all be expressed. The shipped
mapping uses one window, ATR(10), for both the stop and the
trail: stop 3.5xATR(10), trail 11.0xATR(10). The staged
trigger (trail only arms after +1xATR(15)) is also not
expressible — the harness's chandelier trail is live from entry,
but with an 11xATR trail distance it cannot bind until price
has run more than 7.5xATR above entry, which approximates the
source's late-arming behaviour. No fixed target; no max hold
(the source exits only on the stop/trail).
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=10,
    stop_atr_mult=3.5,
    trail_atr_mult=11.0,
    target_atr_mult=None,
    max_hold_bars=None,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 610  # 600-bar Donchian + margin
