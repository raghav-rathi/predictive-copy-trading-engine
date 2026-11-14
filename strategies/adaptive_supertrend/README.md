# Adaptive Supertrend

Supertrend (Olivier Seban) with a Choppiness-Index-adaptive ATR
multiplier — the classic flip system, tightened when the market
trends and widened when it chops.

- **ATR(10)** — Wilder ATR, the volatility gauge
- **CHOP(14)** = 100 × log10( ΣTR(14) / (max H(14) − min L(14)) )
  / log10(14); below 38 the market is trending, above 62 it is
  choppy (Dreiss's published levels)
- **k (per bar)** — chop < 38 → 2.0 (tight: ride the trend);
  chop > 62 → 4.0 (wide: stop flipping on noise); else 3.0 (the
  classic Supertrend default)
- **Bands** — HL2 ± k × ATR(10), rebuilt every bar from that bar's k
- **Supertrend line** — the classic final-band ratchet
  (final upper only falls, final lower only rises) run with the
  per-bar bands; direction flips when close crosses the opposite
  final band
- **Long:** direction flips −1 → +1; **Short:** flips +1 → −1
- **Exit:** the opposite flip (the same event as the opposite entry)
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 200-bar max hold,
  1% risk/trade, 3x leverage

Parameters: ATR n=10, CHOP n=14, k ∈ {2.0, 3.0, 4.0} at chop
thresholds 38 / 62. WARMUP=60 (ATR + Choppiness spin-up, with margin).

The adaptive loop lives in `indicators.py` because
`strategies.base.supertrend` takes a fixed k; the loop logic
(final-band ratchet + direction flip on close through the opposite
band) is identical, only the band inputs vary per bar. With a
constant k the loop reproduces `base.supertrend` exactly (tested).

Usage:

```python
from strategies.data import fetch_candles
from strategies.adaptive_supertrend import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the fixed-k sensitivity check.

Sources: Supertrend (Olivier Seban) —
https://www.investopedia.com/supertrend-indicator-7976167 ;
Choppiness Index (E.W. Dreiss) — same formula as
`strategies/choppiness_index/`.
