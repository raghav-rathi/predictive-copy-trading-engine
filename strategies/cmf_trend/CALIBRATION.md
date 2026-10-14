# Chaikin Money Flow — Calibration

**Shipped:** CMF(21) zero-cross + 200-bar SMA regime filter, 2xATR
stop, 3xATR trail, 240-bar max hold.

**What the numbers say:** −$6,658 combined; BTC PF 0.44 is a blowout.
The 21-bar accumulation window is too slow for 1h — crosses fire after
the move — and the 200-bar filter pins the system to stale trends.
HYPE +3.2% (Sharpe 0.36) is noise, not signal.

**Next experiment (only if revisited):** shorten to CMF(9) and drop
the 200-bar filter on 1h. That tests whether money-flow has any
short-horizon timing value on perps, where "volume" is contract
turnover rather than share accumulation.

**Do not:** keep the 200-bar regime filter on 1h — it answers a
question (multi-week trend) the 21-bar trigger isn't asking.
