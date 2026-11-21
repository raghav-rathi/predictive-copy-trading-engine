# Accumulation/Distribution Line

Marc Chaikin's A/D line: each bar's volume signed by where the close
sits inside the bar's high-low range, cumulated into a running
total. This strategy trades the A/D line's crosses of its own
SMA(20) — long on a cross up, short on a cross down.

## Rules

- **Money flow multiplier:** MFM = ((C - L) - (H - C)) / (H - L),
  in [-1, +1]; H == L -> MFM = 0.
- **Money flow volume:** MFV = MFM * v.
- **A/D line:** AD = cumulative sum of MFV.
- **Signal line:** SMA(20) of AD.
- **Long entry:** AD crosses up through SMA(20) (transition only).
- **Short entry:** AD crosses down through SMA(20) (transition only).
- **Long exit:** AD crosses down through SMA(20).
- **Short exit:** AD crosses up through SMA(20).
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 40 bars (SMA(20) first defined at bar 19).

All computation is causal: MFM/MFV use only the current bar, AD is
a trailing cumulative sum, and the SMA is trailing.

## Sources

- TrendSpider, "Accumulation/Distribution Oscillator":
  https://trendspider.com/learning-center/accumulation-distribution-oscillator/
- Marc Chaikin, Accumulation/Distribution Line.

## Files

- `indicators.py` — MFM, MFV, AD, SMA(20), ATR(14)
- `signals.py` — AD/SMA cross entry/exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_accumulation_distribution.py` — 17 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices

## How to run

From the repo root:

```
python3 -m pytest strategies/accumulation_distribution/test_accumulation_distribution.py -q
python3 strategies/accumulation_distribution/run_backtest.py
```

## Verdict

Loser, worst of the batch: -$16,976.83 combined on 2,304 trades
(PF 0.68, Sharpe -5.56, MaxDD -57.3%). The A/D line whipsaws across
its SMA on 1h bars — ~1 trade per 2.6 bars — and fees ($12,242.78)
do most of the damage. See BACKTEST.md.

Paper only, no live execution.
