# Detrended Price Oscillator

StockCharts ChartSchool's Detrended Price Oscillator (DPO) —
a cycle-measurement tool that removes trend by comparing
price with a displaced moving average.

- **Long:** DPO crosses above 0
- **Short:** DPO crosses below 0
- **Exit:** the opposite cross
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 60-bar max
  hold, 1% risk/trade, 3x leverage (the harness stops sit
  behind the cross itself as a safety net for gap-through
  moves)

Parameters: DPO(20) = close − SMA(close, 20) shifted back
11 bars (displacement = 20/2 + 1 = 11), i.e. DPO[i] =
close[i] − SMA20[i − 11]. ATR(14) in the harness for the
stop/trail. WARMUP=35.

Two readings of DPO exist and only one is tradeable in real
time. StockCharts' centered plotting convention takes the
price at a bar minus the 20-day SMA ending 11 bars in the
future — that uses future data and is not computed here.
This build uses the causal, real-time reading (the MetaStock
"Technical Analysis from A to Z" formula: "subtract the
moving average (n/2)+1 days ago from the closing price"):
the SMA as it stood 11 bars ago, subtracted from the current
close. The two versions are the same series shifted by 11
bars. StockCharts itself notes DPO "is not designed for
momentum signals" — this build trades the zero-line cross
anyway, as specified, and the backtest is the verdict on it.

Usage:

```python
from strategies.detrended_price_osc import indicators, signals, risk

df = indicators.add_indicators(df)  # period=20 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-25 Hyperliquid 1h
(BTC/ETH/HYPE, batch-46 pinned window) results — honest verdict:
a loser on every coin, with a 21–24% win rate — and
CALIBRATION.md for the DPO-period 10/20/40 sensitivity check
and the lookahead audit (no lookahead: the SMA uses closes
through bar i − 11 only).
