# Supertrend + MACD Agreement

Supertrend direction (a trend-following band system) confirmed by
MACD histogram momentum: trade only when the trend filter and the
momentum filter agree, and exit as soon as either one breaks.

## Rules

- **Supertrend(10, 3.0 ATR):** Wilder ATR(10) bands around the
  (high+low)/2 midpoint; the trend flips when the close crosses the
  active band. Direction +1 = bullish (close above the Supertrend
  line), -1 = bearish.
- **MACD(12, 26, 9):** histogram = MACD line − signal line;
  positive = momentum up, negative = momentum down.
- **Long entry:** the first bar where Supertrend is bullish AND the
  MACD histogram is positive (transition into agreement).
- **Short entry:** the mirror (Supertrend bearish AND histogram
  negative).
- **Long exit:** Supertrend flips bearish OR the histogram turns
  negative.
- **Short exit:** Supertrend flips bullish OR the histogram turns
  positive.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 40 bars.

All computation is causal: Supertrend seeds at the first bar with a
valid ATR using only data through that bar, and every signal on bar
i uses data through bar i's close.

## Sources

- TradingView, "Supertrend":
  https://www.tradingview.com/support/solutions/43000594684-supertrend/
- Investopedia, "Moving Average Convergence Divergence (MACD)":
  https://www.investopedia.com/terms/m/macd.asp

## Files

- `indicators.py` — Supertrend (via `strategies.base`) + MACD
- `signals.py` — agreement-transition entries, either-leg exits
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_supertrend_macd.py` — 22 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices + sweep

## How to run

From the repo root:

```
python3 -m pytest strategies/supertrend_macd/test_supertrend_macd.py -q
python3 strategies/supertrend_macd/run_backtest.py
```

Paper only, no live execution.
