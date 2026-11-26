# Connors TPS

Larry Connors & Cesar Alvarez's TPS (Trend, Pullback, Setup)
from "Short Term Trading Strategies That Work" (2008) and
"High Probability ETF Trading", scaled from daily bars to 1h
bars.

- **Trend:** close > SMA(200) for longs, close < SMA(200)
  for shorts — the book's daily 200-bar filter scaled to 200
  1h bars (~8.3 days), stated as an adaptation, not the
  book's daily rule.
- **Long:** RSI(2) below 25 for two consecutive bars (entry
  on the close of the second bar, executed at next-bar open
  by the harness)
- **Short:** RSI(2) above 75 for two consecutive bars
- **Exit:** RSI(2) closes above 70 (long) / below 30
  (short), OR a 10-bar time exit — the book's day-11 exit,
  scaled to 1h and enforced by the harness
  max_hold_bars=10
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 1%
  risk/trade, 3x leverage. The original system has no stop —
  the house 2xATR stop / 3xATR trail is added as a deviation
  required by house risk rules.

Parameters: SMA(200), RSI(2) with entry 25 / 75 and exit 70
/ 30, max hold 10 bars. Exit conditions are levels, not
crosses: the harness checks them every bar while a position
is open, so the first bar RSI(2) closes above 70 (below 30)
exits, exactly as a cross would.

Note on base.rsi: it 0-fills on flat stretches (RSI sits at
0 where only losses are seen, 100 where only gains). After a
pure flat stretch RSI(2) reads 0, which is below the 25
entry level — the two-consecutive-bar rule plus the SMA(200)
trend filter are the guards, and WARMUP = 210 keeps the
spin-up out of the traded window.

Source: Larry Connors & Cesar Alvarez — "Short Term Trading
Strategies That Work" (2008) —
https://tradingstrategyguides.com/tps-trading-strategy/

Usage:

```python
from strategies.connors_tps import indicators, signals, risk

df = indicators.add_indicators(df)  # sma_n=200, rsi_n=2 defaults
sig = signals.add_signals(df)  # entry_low=25.0, entry_high=75.0, exit_high=70.0, exit_low=30.0 defaults
```

See BACKTEST.md for the 2026-03-14 → 2026-11-26 Hyperliquid 1h
(BTC/ETH/HYPE, batch-47 pinned window) results and
CALIBRATION.md for the entry-threshold 20/25/30 sensitivity
check.
