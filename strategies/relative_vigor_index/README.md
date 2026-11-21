# Relative Vigor Index

John Ehlers' Relative Vigor Index ("Cybernetic Analysis for Stocks
and Futures", 2004; first presented in Technical Analysis of Stocks
& Commodities, January 2002): a momentum oscillator that measures
where each bar closes relative to where it opened, scaled by the
bar's range. In an uptrend prices tend to close above the open; in a
downtrend below it. Traded here on RVI/signal-line crosses.

## Rules

- **Numerator:** (c-o) + 2*(c1-o1) + 2*(c2-o2) + (c3-o3), where
  c1/o1 are one bar back, etc.
- **Denominator:** (h-l) + 2*(h1-l1) + 2*(h2-l2) + (h3-l3).
- **RVI:** numerator / denominator (a zero denominator gives 0).
- **Signal:** (RVI + 2*RVI1 + 2*RVI2 + RVI3) / 6.
- **Long entry:** RVI crosses up through signal (transition only).
- **Short entry:** RVI crosses down through signal (transition only).
- **Long exit:** RVI crosses down through signal.
- **Short exit:** RVI crosses up through signal.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 40 bars (RVI first defined at bar 3, signal at bar 6).

All computation is causal: trailing 4-bar windows only, and the
cross uses bars through the current close only.

Note: this is the direct 4-bar SWMA ratio. Some platforms
additionally average the numerator and denominator over 10 bars
before dividing; that variant is not used here — see CALIBRATION.md.

## Sources

- John Ehlers, "Cybernetic Analysis for Stocks and Futures" (Wiley,
  2004); RVI first presented in Technical Analysis of Stocks &
  Commodities, January 2002.
- Bybit Wiki, "Relative Vigor Index (RVI) vs RSI: Differences"
  (formula reference):
  https://www.bybit.com/en/wiki/article/relative-vigor-index-rvi-vs-rsi-differences/

## Files

- `indicators.py` — RVI numerator/denominator, RVI, signal line
- `signals.py` — RVI/signal cross entry/exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_relative_vigor_index.py` — 16 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices

## How to run

From the repo root:

```
python3 -m pytest strategies/relative_vigor_index/test_relative_vigor_index.py -q
python3 strategies/relative_vigor_index/run_backtest.py
```

## Verdict

Worst of the batch: -$25,796.42 combined on 5248 trades (PF 0.61,
Sharpe -10.82, MaxDD -86.4%). RVI crosses its signal almost every
other bar at 1h frequency; gross PnL before fees is about -$8,669
and $17,128 of fees compounds the loss. No edge on this window —
see BACKTEST.md.

Paper only, no live execution.
