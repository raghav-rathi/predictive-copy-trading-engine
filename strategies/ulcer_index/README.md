# Ulcer Index Regime Gate

Breakout entries filtered by Peter Martin's Ulcer Index (1987) — a
pure downside-volatility gauge.

## Mechanism

The Ulcer Index measures only the depth of drawdowns from the
trailing n-bar peak:

- **Percent drawdown** = 100 × (close − max(close, n)) / max(close, n)
- **Ulcer Index** = √(mean(percent-drawdown²)) over n bars

A rising market reads ~0 (prior closes sit just below the trailing
peak); a sharp drop makes it spike. Martin designed it for
stress-free investing: trade only when the gauge reads calm, stand
aside when it reads stressed.

## Why long-only regime gating

The UI is asymmetric by construction: it knows about downside
stress, not upside exhaustion. So it fits a long-only breakout
system as a *regime gate*, not as a directional oscillator:

- **Long:** prior-bar ulcer < 5.0 (calm regime) AND close crosses
  above the prior 20-bar Donchian high. The gate reads the *prior*
  bar because a breakout to a new high becomes the trailing peak on
  its own bar, inflating the current-bar read — gating on the
  current bar would veto every entry.
- **Exit:** close crosses below the prior 10-bar Donchian low, OR
  ulcer > 10.0 (panic spike — the calm-regime premise is broken,
  get out even if price hasn't hit the exit level).
- **No shorts** (allow_shorts=False): the UI says nothing about
  upside exhaustion, so there is nothing to short on.
- **Risk:** 1.5xATR hard stop, 2xATR chandelier trail, no fixed
  target (exits are regime/signal-driven), 120-bar (~5-day) max
  hold, 1% risk/trade, 3x leverage.

Parameters: n=14 (fixed a priori), entry Donchian 20, exit Donchian
10, calm < 5.0, panic > 10.0, ATR(14). WARMUP=60.

Usage:

```python
from strategies.ulcer_index import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))  # n=14 default
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the n=7/14/28 sensitivity check.

Sources:

- Peter Martin's Ulcer Index —
  https://en.wikipedia.org/wiki/Ulcer_index
- Indicator mechanics / usage notes —
  https://www.tradingview.com/support/solutions/43000564954
