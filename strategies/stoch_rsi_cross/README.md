# Stochastic RSI Crossover

Tushar Chande & Stanley Kroll's StochRSI (1994): apply the
stochastic oscillator formula to RSI values instead of prices, for
a faster, more sensitive momentum oscillator. This strategy trades
%K/%D crosses inside the oversold (< 20) and overbought (> 80)
zones and exits on the opposite cross.

## Rules

- **RSI(14)** of the close (Wilder).
- **%K** = 100 × (RSI − min RSI last 14) / (max RSI last 14 − min RSI
  last 14); a zero-range window scores 50; clipped to [0, 100].
- **%D** = SMA(3) of %K.
- **Long entry:** %K crosses up through %D while %K < 20
  (transition only).
- **Short entry:** %K crosses down through %D while %K > 80
  (transition only).
- **Long exit:** %K crosses down through %D.
- **Short exit:** %K crosses up through %D.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 40 bars (first %D at bar 15).

All computation is causal: trailing windows only, no lookahead.

## Sources

- Tushar Chande & Stanley Kroll, *The New Technical Trader*
  (1994); StochRSI definition:
  https://www.investopedia.com/terms/s/stochrsi.asp

## Files

- `indicators.py` — RSI(14), %K, %D
- `signals.py` — zone-filtered %K/%D cross entry/exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_stoch_rsi_cross.py` — 16 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices

## How to run

From the repo root:

```
python3 -m pytest strategies/stoch_rsi_cross/test_stoch_rsi_cross.py -q
python3 strategies/stoch_rsi_cross/run_backtest.py
```

## Verdict

Loser, worst of the batch: −$14,863.94 combined on 1,493 trades
(PF 0.48, Sharpe −8.51, MaxDD −50.2%). The %K/%D cross whipsaws
on 1h bars — 1,296 of 1,493 exits are the opposite cross, so
positions churn to death on $8,664.52 of fees. See BACKTEST.md.

Paper only, no live execution.
