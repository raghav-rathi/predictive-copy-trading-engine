# Rolling VWAP Cross

Trade the classic VWAP-cross setup — but session-less. VWAP is the
institutional benchmark: block desks and execution algos target it,
so a decisive cross of price through VWAP on heavy volume is a
momentum-handoff signal (sellers' or buyers' benchmark is breaking).

On equities VWAP anchors to the session open. Crypto trades 24/7,
so there is no session to anchor to — this strategy uses a
trailing 24-bar (1 day on 1h bars) VWAP instead:

- **VWAP** = rolling_sum(tp × v, 24) / rolling_sum(v, 24),
  tp = (h + l + c) / 3. Zero-volume windows fall back to tp.
- **Slope** = vwap − vwap.shift(3): is the benchmark itself
  rising or falling?
- **vol_ratio** = v / SMA(v, 20): is this bar printing on real
  flow?

## Entries (filters are the strategy — a bare cross is noise)

- **Long:** close crosses *above* the VWAP AND vwap_slope > 0
  (the benchmark itself is rising — buyers are lifting the
  average transaction price) AND vol_ratio > 1.2 (the cross
  prints on 1.2× average volume — institutional participation,
  not a range flicker).
- **Short:** exact mirror — cross below, slope < 0, vol_ratio > 1.2.

## Exits

Pure opposite crosses, no filters — once the trade is on, the
exit should be trigger-happy, not gated:

- **long_exit:** close crosses below the VWAP
- **short_exit:** close crosses above the VWAP

## Risk

1.5xATR hard stop, 2xATR chandelier trail, no fixed target (the
opposite cross is the exit), 72-bar (~3-day) max hold — a VWAP
cross that hasn't resolved in three days was noise, not a
handoff. 1% risk/trade, 3x leverage cap, long/short symmetric.

Parameters: VWAP 24, slope lookback 3, vol filter 1.2×. All fixed
a priori; no optimization. WARMUP=60.

Usage:

```python
from strategies.vwap_cross import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the a-priori calibration rationale.

Sources:

- VWAP cross mechanics —
  https://algotradinglib.com/en/pedia/v/vwap_cross.html
- VWAP explained / how traders use it —
  https://bingx.com/en/learn/article/vwap-explained-what-it-is-how-traders-use-it
