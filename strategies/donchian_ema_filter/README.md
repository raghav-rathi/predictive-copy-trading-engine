# Donchian EMA Filter

Richard Donchian / Turtle System 1: trade the breakout of the
20-bar channel, but only in the direction of the 50-bar trend —
and exit on the Turtle 10-bar reversal level.

## Rules

- **Donchian(20):** upper = highest high of the PREVIOUS 20 bars,
  lower = lowest low of the previous 20 bars (current bar excluded).
- **Long entry:** close above the prior 20-bar high AND above EMA(50).
- **Short entry:** close below the prior 20-bar low AND below EMA(50).
- **Long exit:** close below the prior 10-bar low (Turtle System 1 exit).
- **Short exit:** close above the prior 10-bar high.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

All computation is causal: breakout and exit levels on bar i use
bars before i only (shifted by one); EMA(50) uses closes through
bar i.

## Sources

- PatternsWizard, "Donchian Channel":
  https://patternswizard.com/donchian-channel/
- InvestingPaths, "Turtle Trading Rules Tested":
  https://investingpaths.com/turtle-trading-rules-tested

## Verdict: LOSER

Backtest (2026-03-14 → 2026-11-20, BTC/ETH/HYPE 1h, $10k per coin):
combined **-$3,120.47 on 660 trades, PF 0.90, Sharpe -0.75,
MaxDD -15.1%** — BTC -$2,153.12, HYPE -$1,121.33, ETH nominally
flat +$153.98 (PF 1.02, noise). 591 of 660 trades end on the
harness stop vs 69 on the Turtle signal exit: 1h breakouts fail
into the stop before the 10-bar exit can act. Gross of fees the
strategy is ~breakeven, so this is largely a fee-drag story — but
with PF 0.90 there is no edge underneath the fees either.
See BACKTEST.md for the full table.

## Files

- `indicators.py` — Donchian levels, EMA(50), Turtle exit levels, ATR
- `signals.py` — entry/exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_donchian_ema_filter.py` — 19 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices + sweep

## How to run

From the repo root:

```
python3 -m pytest strategies/donchian_ema_filter/test_donchian_ema_filter.py -q
python3 strategies/donchian_ema_filter/run_backtest.py
```

Paper only, no live execution.
