# Bollinger Bands %b Mean Reversion

Bollinger Bands(20, 2.0) %b mean reversion: price tagging the
outer band tends to revert to the middle band (SMA(20)). This
strategy buys the lower-band tag and shorts the upper-band tag,
exiting on the return to the middle band.

## Rules

- **Bands:** middle = SMA(20) of close; upper/lower = middle
  +/- 2 * rolling sample standard deviation. %b = (close - lower)
  / (upper - lower).
- **Long entry:** close below the lower band (%b <= 0).
- **Short entry:** close above the upper band (%b >= 1).
- **Long exit:** close back at/above the middle band.
- **Short exit:** close back at/below the middle band.
- No extra filter — the band tag IS the signal.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 40 bars.

All computation is causal: every band value on bar i uses closes
through bar i only.

## Sources

- John Bollinger, "Bollinger on Bollinger Bands" (McGraw-Hill, 2001):
  https://www.bollingerbands.com/
- Investopedia, "Bollinger Bands":
  https://www.investopedia.com/terms/b/bollingerbands.asp

## Files

- `indicators.py` — Bollinger Bands + %b + ATR(14)
- `signals.py` — entry/exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_bollinger_reversion.py` — 18 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices + sweep

## How to run

From the repo root:

```
python3 -m pytest strategies/bollinger_reversion/test_bollinger_reversion.py -q
python3 strategies/bollinger_reversion/run_backtest.py
```

## Verdict

LOSER on the shipped window: -$17,011.55 on 1,104 trades
(combined Sharpe -6.27, MaxDD -57.4%). Lower-band tags in a
downtrending window keep extending instead of reverting, and
most trades end on the harness stop. See BACKTEST.md.

Paper only, no live execution.
