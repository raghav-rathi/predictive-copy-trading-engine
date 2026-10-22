# DEMA Trend Cross

Trend-capture on Patrick Mulloy's Double Exponential Moving Average
(TASC, Jan 1994) — a smoothed trend line with most of the plain-EMA
lag removed.

## Mechanism

Mulloy's DEMA applies the EMA twice and subtracts the lag out:

- **EMA1** = EMA(close, n), **EMA2** = EMA(EMA1, n)
- **DEMA** = 2×EMA1 − EMA2

The second pass isolates the EMA's lag component; subtracting it (and
doubling the first pass) yields a line that tracks price roughly twice
as fast as the plain EMA without adding jitter. On a clean step move,
DEMA(21) reaches the new level in roughly half the bars of EMA(21)
(see `test_dema_lag_less_than_ema_on_step`).

- **Long:** DEMA(21) crosses above DEMA(55) — the lag-reduced line
  turns up relative to the slow anchor
- **Short:** DEMA(21) crosses below DEMA(55)
- **Exit:** the opposite cross (a cross back means the trend read
  failed)
- **Risk:** 2xATR hard stop, 2.5xATR chandelier trail, 200-bar max
  hold (~8.3 days of 1h bars), 1% risk/trade, 3x leverage. No fixed
  target — exits are cross-driven.

Parameters: fast=21, slow=55, ATR(14) for stop/trail. WARMUP=140
(DEMA(55) spin-up ~108 bars, with margin).

Usage:

```python
from strategies.data import fetch_candles
from strategies.dema_trend import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))  # fast=21, slow=55 default
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the (10,30)/(21,55)/(34,89) sensitivity check. The
shipped (21,55) pair was fixed a priori, not selected from the sweep.

Source: DEMA (Patrick Mulloy, TASC Jan 1994) —
https://forex-station.com/download/file.php?id=3525533&sid=69c919d7260e3323d4ab1f31c1bb8753
