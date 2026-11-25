# Traders Dynamic Index

Dean Malone's Traders Dynamic Index (TDI) — RSI with three
overlaid lines and volatility bands, read as a single
momentum panel.

- **Long:** price line crosses above signal line AND price
  line is above the base line AND the base line is above 50
- **Short:** price line crosses below signal line AND price
  line is below the base line AND the base line is below 50
- **Exit:** the opposite price/signal cross (no base-line
  condition on the exit)
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 60-bar max
  hold, 1% risk/trade, 3x leverage (the harness stops sit
  behind the cross itself as a safety net for gap-through
  moves)

Parameters: RSI(13) (Wilder); price line = SMA(RSI, 2);
signal line = SMA(RSI, 7); market base line = SMA(RSI, 34);
volatility bands = base ± 1.6185 × std(RSI, 34). The bands
are computed and stored for context; the shipped signals
use the cross plus the base-line level filter only. ATR(14)
in the harness for the stop/trail. WARMUP=40.

Usage:

```python
from strategies.tdi_traders_dynamic import indicators, signals, risk

df = indicators.add_indicators(df)  # rsi_n=13 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-25 Hyperliquid 1h
(BTC/ETH/HYPE, batch-46 pinned window) results — honest verdict:
a loser on every coin, with a 26–33% win rate — and
CALIBRATION.md for the RSI-period 10/13/21 sensitivity check
and the lookahead audit (no lookahead: Wilder RSI is a
causal ewm; the SMAs and rolling std use data through bar i
only).
