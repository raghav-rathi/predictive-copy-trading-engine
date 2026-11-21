# Donchian Channel Breakout

Richard Dennis / Turtle Traders Donchian(20) breakout: buy the first
close above the highest high of the prior 20 bars, short the first
close below the lowest low of the prior 20 bars, and exit on the
Turtle 10-bar rule.

## Rules

- **Donchian channel:** upper = highest high of the prior 20 bars
  (bars i-20..i-1); lower = lowest low of the prior 20 bars.
- **Long entry:** close > upper, transition only (previous bar's
  close was NOT above the then-current upper).
- **Short entry:** close < lower, transition only.
- **Long exit:** close < lower, OR close < lowest low of the prior
  10 bars (Turtle 10-bar exit).
- **Short exit:** close > upper, OR close > highest high of the
  prior 10 bars.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 40 bars (channel needs 20 bars + 1 shift).

All computation is causal: channel levels use bars i-20..i-1 only,
and the close on bar i is compared against them.

## Sources

- PatternsWizard, "Donchian Channel: Definition & Turtle Rules":
  https://patternswizard.com/donchian-channel/

## Files

- `indicators.py` — Donchian channel, Turtle 10-bar exit levels, ATR(14)
- `signals.py` — transition-only entry / level exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_donchian_breakout.py` — 15 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices

## How to run

From the repo root:

```
python3 -m pytest strategies/donchian_breakout/test_donchian_breakout.py -q
python3 strategies/donchian_breakout/run_backtest.py
```

## Verdict

Loser: -$2,097.76 combined on 667 trades (PF 0.93, Sharpe -0.48).
Only ETH is green (+$382.08); 595 of 667 exits are harness stops,
not signal exits. No edge on this window — see BACKTEST.md.

Paper only, no live execution.
