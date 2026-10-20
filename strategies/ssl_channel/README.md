# SSL Channel

The SSL Channel: a two-line SMA high/low channel whose line "flips"
above/below price to mark regime changes.

- **ssl_up** = SMA(High, 10), **ssl_dn** = SMA(Low, 10)
- **Bullish** when Close > ssl_up; **bearish** when Close < ssl_dn;
  between the lines the prior regime persists (state machine)
- **Long** on the flip to bullish (close crosses above the active SSL
  line); **short** on the flip to bearish
- **Exit:** the opposite flip — the channel manages the trade
- **Risk:** 2xATR hard stop, no trail, no target, 200-bar max hold,
  1% risk/trade, 3x leverage

Parameters: `SSL_LEN=10` (see `indicators.py`).

See BACKTEST.md for the 2026-03-14 → 2026-10-20 Hyperliquid 1h
(BTC/ETH/HYPE) results — this batch is an honest loser — and
CALIBRATION.md for the 6/10/20 channel-length sweep.

Usage:

```python
from strategies.ssl_channel import SPEC
from strategies.backtest import run_backtest
sig = SPEC.add_signals(SPEC.add_indicators(df))
res = run_backtest(sig, SPEC.risk, coin="BTC", warmup=SPEC.warmup_bars, use_funding=False)
```
