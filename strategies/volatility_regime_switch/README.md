# Volatility Regime Switch

ATR(14) percentile rank over the trailing 100 bars decides
whether volatility is expanding or compressing, and the
strategy trades the regime it is in: breakouts in expansion,
fades in compression.

## Rules

- **Regime:** ATR(14) percentile rank over the trailing 100
  bars (fraction of the last 100 ATR values ≤ the current ATR).
  Percentile > 0.60 is expansion, < 0.40 is compression,
  0.40–0.60 is the middle regime (no entries, no signal exits).
- **Expansion — Donchian(20) breakout:** long on a close above
  the prior 20-bar high, short on a close below the prior
  20-bar low. The prior high/low EXCLUDE the current bar: the
  Donchian level as of the previous bar's close. A trailing
  high that included the current bar could never be broken by
  the close, so the exclusion is load-bearing.
  Exit on a close back inside the channel midpoint
  ((prev_high + prev_low) / 2), or on the opposite break.
- **Compression — Bollinger(20, 2) fade:** long on a close below
  the lower band, short on a close above the upper band. Exit
  on a close back to the mid (above the mid for a long, below
  the mid for a short).
- Exits follow the regime in force on the signal bar, so a trade
  opened in one regime is exited by the new regime's rules if
  the regime flips mid-trade. In the middle regime there is no
  signal exit; the harness stop / trail / max hold carries the
  position.
- The harness risk layer's 2xATR stop / 2.5xATR trail also
  applies. Max hold 120 bars.
- Warmup 120 bars (100-bar percentile + ATR/Donchian/Bollinger
  warmup; `atr_pct` is NaN until bar 112 because ATR itself
  needs 14 bars).

## Sources

- ForTraders, "Momentum vs Mean Reversion Strategies for
  Challenges":
  https://fortraders.com/blog/momentum-vs-mean-reversion-strategies-for-challenges

## Files

- `indicators.py` — ATR(14), ATR percentile rank, Donchian(20)
  (prior-bar levels), Bollinger(20, 2)
- `signals.py` — regime-gated breakout / fade entries and exits
- `risk.py` — batch-standard risk config, warmup 120
- `test_volatility_regime_switch.py` — 17 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` / `CALIBRATION.md` — results and parameter notes

## How to run

From the repo root:

```
python3 -m unittest strategies.volatility_regime_switch.test_volatility_regime_switch -v
python3 strategies/volatility_regime_switch/run_backtest.py
```

Paper only, no live execution.
