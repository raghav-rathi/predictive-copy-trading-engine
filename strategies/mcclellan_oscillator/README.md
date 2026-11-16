# McClellan Oscillator

Breadth oscillator on a single-asset candle-count proxy for
advance/decline data.

- **RANA:** 1000·(up − down)/(up + down) over a rolling 24-bar
  window (up = close > open, down = close < open, doji bars neutral)
- **Oscillator:** EMA19(RANA) − EMA39(RANA)
- **Summation index:** cumulative sum of the oscillator
- **Long:** oscillator crosses above 0 after dipping below −50 in
  the prior 10 bars, with the summation index rising
- **Short:** oscillator crosses below 0 after exceeding +50 in the
  prior 10 bars, with the summation index falling
- **Exit:** oscillator crosses back through 0, or the summation
  index turns against the position
- **Risk:** 1.5xATR stop, 2.5xATR target, 48-bar max hold,
  1% risk/trade, 3x leverage

Parameters: window=24, EMA 19/39, excursion ±50, lookback 10.
WARMUP=60 (EMA39 spin-up + RANA window + margin).

The "|osc| < 10: no trade" filter is satisfied by construction:
entries require a prior excursion beyond ±50, so |osc| exceeded
10 by a wide margin on the way into the trade.

Usage:

```python
from strategies.data import fetch_candles
from strategies.mcclellan_oscillator import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=365)
sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the 10/21 – 19/39 – 30/50 sensitivity check.

Sources: McClellan Oscillator (AAII) —
https://www.aaii.com/journal/article/347760-looking-beyond-price-trends-with-the-mcclellan-oscillator
and https://patternswizard.com/mcclellan-oscillator/

## Honest caveats

- **Single-asset candle-count proxy, not true advance/decline
  data.** The real McClellan Oscillator is built from exchange-wide
  advancing vs declining issues. Here one asset's up/down candle
  counts stand in for breadth — and the backtest says the proxy
  does not work: combined −$3,980 on 190 trades, win rate 30–32%
  on every coin, profit factor 0.64–0.71.
- Up/down candle counts on a single asset are mostly a relabeling
  of that asset's own returns, so the "breadth thrust" is a lagged
  momentum signal that buys tops and sells bottoms.
- Single 8-month crypto window; no out-of-sample evidence.
