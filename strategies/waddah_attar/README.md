# Waddah Attar Explosion

Ahmad Waddah Attar's momentum-explosion engine: trade only when
momentum is accelerating hard enough to clear a volatility-scaled
"dead zone".

- **macd** = EMA(Close, 20) − EMA(Close, 40)
- **hist** = 150 × (macd − macd.shift(1)) — momentum acceleration,
  sensitivity 150
- **explosion line** = 2.0 × stdev(hist, 20) — volatility-scaled
  momentum band
- **dead zone** = 3.7 × ATR(100) — trades print only when both the
  histogram and the explosion line are above it
- **Long:** hist > 0 AND hist rising AND hist > explosion AND
  explosion rising AND hist > dead AND explosion > dead
  (short side mirrors with hist < 0, falling)
- **Exit:** histogram crosses back under the explosion line (momentum
  died); long exits on hist < explosion, short on hist > −explosion
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, no target,
  200-bar max hold, 1% risk/trade, 3x leverage

Parameters: `SENS=150`, `EXP_MULT=2.0`, `EXP_LEN=20`,
`DEAD_MULT=3.7`, `DEAD_ATR_N=100` (see `indicators.py`).

See BACKTEST.md for the 2026-03-14 → 2026-10-20 Hyperliquid 1h
(BTC/ETH/HYPE) results — this batch is an honest loser — and
CALIBRATION.md for the 100/150/200 sensitivity sweep.

Usage:

```python
from strategies.waddah_attar import SPEC
from strategies.backtest import run_backtest
sig = SPEC.add_signals(SPEC.add_indicators(df))
res = run_backtest(sig, SPEC.risk, coin="BTC", warmup=SPEC.warmup_bars, use_funding=False)
```
