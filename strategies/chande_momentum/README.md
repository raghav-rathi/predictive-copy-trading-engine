# Chande Momentum Oscillator

Tushar Chande's CMO(14): a bounded momentum oscillator built from
the raw sums of up-close and down-close moves over 14 bars. This
strategy trades the exit from Chande's ±50 extremes — long when the
oscillator crosses back up through -50, short when it crosses back
down through +50.

## Rules

- **CMO(14):** 100 * (Su - Sd) / (Su + Sd), where Su / Sd are the
  sums of up / down close-to-close moves over the trailing 14 bars.
  Zero denominator (flat window) -> CMO = 0. Range -100 to +100.
- **Long entry:** CMO crosses up through -50 (transition only).
- **Short entry:** CMO crosses down through +50 (transition only).
- **Long exit:** CMO crosses down through +50.
- **Short exit:** CMO crosses up through -50.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 40 bars (CMO first defined at bar 14).

All computation is causal: rolling sums are trailing, and the CMO
on bar i uses closes through bar i only.

## Sources

- TrendSpider, "Chande Momentum Oscillator":
  https://trendspider.com/learning-center/chande-momentum-oscillator/
- Tushar Chande with Stanley Kroll, *The New Technical Trader* (1994).

## Files

- `indicators.py` — CMO(14), ATR(14)
- `signals.py` — ±50 cross entry/exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_chande_momentum.py` — 17 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices

## How to run

From the repo root:

```
python3 -m pytest strategies/chande_momentum/test_chande_momentum.py -q
python3 strategies/chande_momentum/run_backtest.py
```

## Verdict

Loser: -$5,753.29 combined on 587 trades (PF 0.80, Sharpe -1.89).
All three coins lose; 475 of 587 exits are harness stops. The ±50
mean-reversion cross does not pay on 1h crypto in this window — see
BACKTEST.md.

Paper only, no live execution.
