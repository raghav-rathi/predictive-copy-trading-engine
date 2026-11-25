# Percentage Price Oscillator

The Percentage Price Oscillator (PPO) is MACD expressed in
percentage terms: the gap between the 12- and 26-period EMAs
divided by the slow EMA, so readings are comparable across
securities and price levels (StockCharts ChartSchool; Gerald
Appel lineage via MACD).

- **Long:** PPO crosses above its 9-period EMA signal line
  while PPO > 0 (momentum turning up inside an uptrend)
- **Short:** PPO crosses below its signal line while PPO < 0
- **Exit:** the opposite signal-line cross
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 60-bar max
  hold, 1% risk/trade, 3x leverage (the harness stops sit
  behind the PPO cross itself as a safety net for gap-through
  moves)

Parameters: EMA(12), EMA(26), signal EMA(9) — the StockCharts
standard. PPO = 100 × (EMA(12) − EMA(26)) / EMA(26); histogram
= PPO − signal. ATR(14) in the harness for the stop/trail.

Usage:

```python
from strategies.ppo_oscillator import indicators, signals, risk

df = indicators.add_indicators(df)  # fast=12, slow=26, signal=9 defaults
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-25 Hyperliquid 1h
(BTC/ETH/HYPE, batch-46 pinned window) results and
CALIBRATION.md for the signal-period 5/9/14 sensitivity check
and the lookahead audit. No parameter was tuned to PnL.

Source: StockCharts ChartSchool, "Percentage Price Oscillator" —
https://chartschool.stockcharts.com/~gitbook/pdf?page=9QwAOEXf9dmW4Fkyz4Yb&only=yes&limit=100
(verified via search 2026-11-25; confirms the 12/26/9 standard,
the signal line as a 9-day EMA of PPO, and the histogram as
PPO minus signal).
