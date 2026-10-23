# Engulfing Pattern Reversal

The classic two-candle reversal pattern, traded the way the canon
demands: **only with the trend**, on the **closed** engulfing candle,
never intrabar.

## Mechanism

A bullish engulfing is a green candle (close > open) whose *body*
fully covers the prior red candle's body:

- current close ≥ prior open
- current open ≤ prior close

Wicks are ignored on purpose: a bar whose wicks engulf but whose
body doesn't is an indecision bar, not a rejection bar. A doji
(close == open) can never be an engulfing bar. The bearish mirror
swaps the sides.

Signals:

- **long_entry** = bullish_eng AND close > EMA(20) — dip-buy the
  engulfing in an uptrend
- **short_entry** = bearish_eng AND close < EMA(20) — rally-sell the
  engulfing in a downtrend
- **long_exit** = bearish_eng; **short_exit** = bullish_eng — the
  pattern's own negation kills the trade
- The trend filter reads the engulfing bar's own close vs EMA(20)
  at that bar's close (both known at bar close — no lookahead);
  the harness executes at the next bar's open

The pattern canon stresses that engulfings are location- and
trend-dependent: the raw pattern alone is not a trade. Hence the
EMA(20) gate (dip-buys in uptrends, rally-sells in downtrends).

## Risk

1.5xATR hard stop, 2xATR chandelier trail, no fixed target (exits
are signal-driven), 48-bar (~2-day) max hold, 1% risk/trade, 3x
leverage cap. Both directions allowed — the pattern is symmetric.
Costs: 0.045% taker fee + 0.01% slippage per side. WARMUP=60.

Parameters fixed a priori: body-engulf definition, EMA(20) trend
filter. No optimization.

Usage:

```python
from strategies.engulfing_pattern import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results —
the honest verdict is a loser — and CALIBRATION.md for the
a priori parameter note.

Sources:

- Halley Tech — Reversal Candlestick Patterns (act on close,
  location, trend alignment):
  https://halleytech.substack.com/p/reversal-candlestick-patterns
