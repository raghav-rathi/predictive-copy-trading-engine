# Volume-Weighted RSI

Wilder RSI(14) computed on a rolling volume-weighted typical price
instead of the plain close: bars where big volume traded count more
in the price the RSI is measured on. The idea is that an
oversold/overbought reading backed by heavy volume means more than
one printed on thin volume.

## Rules

- **Typical price:** tp = (h + l + c) / 3 per bar.
- **VWTP(14):** sum(tp * v over the last 14 bars) / sum(v over the
  last 14 bars). If the rolling 14-bar volume sum is exactly 0,
  VWTP falls back to the plain close.
- **VW-RSI:** Wilder RSI(14) on the VWTP series.
- **Long entry:** VW-RSI crosses below 30.
- **Short entry:** VW-RSI crosses above 70.
- **Long exit:** VW-RSI crosses back above 50.
- **Short exit:** VW-RSI crosses back below 50.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 40 bars.

All computation is causal: every value on bar i uses data through
bar i's close only.

## Sources

- Wilder RSI (Investopedia):
  https://www.investopedia.com/terms/r/rsi.asp
- The volume-weighted typical price is the standard VWAP-style
  weighting applied to a 14-bar rolling window; no single canonical
  source — the construction is stated in full above.

## Verdict: LOSER

Backtest (2026-03-14 → 2026-11-20, BTC/ETH/HYPE 1h, $10k per coin):
combined **-$4,062.61 on 510 trades, PF 0.84, Sharpe -1.67,
MaxDD -20.0%** — all three coins lose (BTC -$2,145.48, ETH
-$1,178.31, HYPE -$738.82). Stops end 335 of 510 trades vs 175 on
the RSI-50 signal exit: entries run into the stop before the RSI
unwinds. See BACKTEST.md for the full table.

## Files

- `indicators.py` — VWTP + VW-RSI + ATR
- `signals.py` — entry/exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_volume_weighted_rsi.py` — 19 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices + sweep

## How to run

From the repo root:

```
python3 -m pytest strategies/volume_weighted_rsi/test_volume_weighted_rsi.py -q
python3 strategies/volume_weighted_rsi/run_backtest.py
```

Paper only, no live execution.
