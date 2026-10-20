# VIX Fix Fear-Spike Mean Reversion

Larry Williams' VIX Fix: a price-derived fear gauge, no options data
needed.

- **WVF** = 100 × (Highest(High, 22) − Low) / Highest(High, 22), with a
  Bollinger Band (length 20, mult 2.0) drawn on it
- **Long** when WVF crosses **above the upper band** (extreme fear
  spike) — the classic Williams market-bottom setup
- **Long exit** when WVF crosses back **below the band midline** (the
  fear spike deflated), or the 24-bar max hold / 2xATR stop fires
- **Short (inverse leg):** iWVF = 100 × (High − Lowest(Low, 22)) /
  Lowest(Low, 22); short when iWVF crosses above *its* upper band
  (extreme greed / blow-off), symmetric midline exit. This inverse leg
  is the less-reliable published variant — documented, not endorsed
- **Risk:** 2xATR hard stop, no trail, no target, 24-bar max hold,
  1% risk/trade, 3x leverage

Parameters: `WVF_LEN=22`, `BB_LEN=20`, `BB_MULT=2.0` (see
`indicators.py`).

See BACKTEST.md for the 2026-03-14 → 2026-10-20 Hyperliquid 1h
(BTC/ETH/HYPE) results — this batch is an honest loser — and
CALIBRATION.md for the 14/22/30 WVF-length sensitivity check.

Usage:

```python
from strategies.vix_fix import SPEC
from strategies.backtest import run_backtest
sig = SPEC.add_signals(SPEC.add_indicators(df))
res = run_backtest(sig, SPEC.risk, coin="BTC", warmup=SPEC.warmup_bars, use_funding=False)
```
