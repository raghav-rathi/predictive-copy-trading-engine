# Elliott Wave Count

A strict, mechanical Elliott count over confirmed 5-bar pivots — no
discretionary relabelling. Hard rules only:

- **Wave 2** must retrace 38.2–61.8% of wave 1 (never 100%+)
- **Wave 3** is never the shortest — checked when wave 3 completes
  (at the wave-4 pivot): if wave-3 length < wave-1 length the count
  is invalid and the trade exits
- **Wave 4** never overlaps wave-1 territory — a close inside wave-1's
  range after entry is an invalidation exit
- **Wave 5** target is the 161.8% extension of wave 1

- **Long:** valid waves 1–2 counted, enter on a close above the
  wave-1 high (wave-3 breakout)
- **Short:** mirror image (close below the wave-1 low)
- **Exit:** wave-4 overlap invalidation, the 161.8% wave-5 target, a
  wave-3-shortest invalidation, or price under the wave-4 low
- **Risk:** 2xATR stop (≈ the wave-2 extreme — see risk.py), 3xATR
  target (1.5R), 96-bar max hold, 1% risk/trade, 3x leverage

Parameters: pivot_n=5, retracement band 38.2–61.8%, extension 161.8%.
WARMUP=100.

Usage:

```python
from strategies.data import fetch_candles
from strategies.elliott_wave_count import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the pivot-size sensitivity check.

Source: Elliott Wave Theory —
https://www.rabofund.com/blogs/what-is-elliott-wave-theory-a-practical-guide-for-forex-traders

## Honest caveats

- Live wave counts are ambiguous and the strict rules prune most
  candidates: 34 trades across three coins in 8 months (HYPE managed
  exactly one). That is the design working as specified, not a bug —
  but it means the sample is far too thin to claim any edge.
- Combined -$44 on 34 trades is break-even noise, not a result.
  BTC is +$58, ETH -$160, HYPE +$58 on a single trade.
- The wave-3-shortest rule can only be checked when wave 3 completes,
  and the wave-5 target only exists once wave 4 confirms — a count
  that stalls mid-wave just sits until the 96-bar max hold.
- Single 8-month crypto window; no out-of-sample evidence.
