# Schwager Volatility Ratio

Fade wide-ranging bars. Schwager's VR = true range / EMA of the prior
true ranges (14); the current bar is excluded from the EMA, so a wide
bar cannot dilute its own reading. VR > 2.0 marks a bar whose range is
more than twice its recent norm — treated here as exhaustion, not
breakout.

- **Long:** VR > 2.0 on a bearish bar (close in the lower 25% of the
  bar, 5-bar return negative)
- **Short:** VR > 2.0 on a bullish bar (close in the upper 25% of the
  bar, 5-bar return positive)
- **Exit:** the opposite wide bar (a bullish VR > 2.0 bar exits a
  long), the 1.5R target, or the 10-bar time exit
- **Risk:** 2xATR stop (≈ just beyond the wide bar's extreme — see
  risk.py), 3xATR target (1.5R), 10-bar max hold, 1% risk/trade,
  3x leverage

Parameters: VR EMA 14, threshold 2.0, position quarter 25%, 5-bar
return context. WARMUP=30.

Execution note: the spec says "enter next 1h close", but the harness
executes signal entries at the next bar's *open*, so the effective
entry is the open after the wide bar rather than that bar's close.
One entry per wide bar is automatic: each wide bar emits a single-bar
signal and the harness holds one position at a time.

Usage:

```python
from strategies.data import fetch_candles
from strategies.schwager_volatility_ratio import indicators, signals, risk

df = fetch_candles("BTC", "1h", lookback_days=260)
sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the VR-threshold sensitivity check.

Source: Schwager Volatility Ratio —
https://www.incrediblecharts.com/indicators/volatility_ratio_schwager.php

## Honest caveats

- This fades wide bars, so it loses in runaway trends where the wide
  bar is the start of a leg, not its end. The batch window (Mar–Nov
  2026, including the early-Nov selloff) is exactly that regime: the
  strategy is the worst of the batch at -$8,810 combined, red on all
  three coins with Sharpe below -2.3 everywhere.
- Win rate ~43% with a 1.5R target should be roughly breakeven; the
  -$17.11/trade expectancy says the wins are small and the losses
  run to the stop far more often than the target.
- Single 8-month crypto window; no out-of-sample evidence.
