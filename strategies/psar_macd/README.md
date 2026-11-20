# Parabolic SAR + MACD Agreement

Wilder's Parabolic SAR flip (a trailing reversal point) confirmed
by the MACD line-vs-signal: trade only the flips where momentum
already agrees, and exit on the next flip or a MACD cross against.

## Rules

- **Parabolic SAR (step 0.02, max AF 0.20):** seeded long from
  bar 0 (SAR = low[0], EP = high[0], AF = 0.02); SAR advances by
  AF × (EP − SAR), clamped to the prior two lows (long) / highs
  (short); a close through the SAR flips the trend and resets the
  SAR to the prior extreme point.
- **MACD(12, 26, 9):** line vs signal supplies the agreement
  filter.
- **Long entry:** PSAR flips to below price AND the MACD line is
  above its signal on that bar.
- **Short entry:** PSAR flips to above price AND the MACD line is
  below its signal on that bar.
- **Long exit:** opposite PSAR flip OR MACD line crosses below
  signal.
- **Short exit:** opposite PSAR flip OR MACD line crosses above
  signal.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 40 bars.

All computation is causal: the PSAR seed uses bar 0 only, and
every signal on bar i uses data through bar i's close.

## Sources

- Investopedia, "Parabolic SAR":
  https://www.investopedia.com/terms/p/parabolicindicator.asp
- Investopedia, "Moving Average Convergence Divergence (MACD)":
  https://www.investopedia.com/terms/m/macd.asp

## Files

- `indicators.py` — Parabolic SAR (implemented from scratch) + MACD
- `signals.py` — flip + MACD-agreement entries, flip/cross exits
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_psar_macd.py` — 23 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices + sweep

## How to run

From the repo root:

```
python3 -m pytest strategies/psar_macd/test_psar_macd.py -q
python3 strategies/psar_macd/run_backtest.py
```

Paper only, no live execution.
