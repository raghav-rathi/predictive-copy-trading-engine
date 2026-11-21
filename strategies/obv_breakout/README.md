# On-Balance Volume Breakout

Joseph Granville's On-Balance Volume breakout: trade the first close
of OBV beyond its own prior-20-bar extreme — volume flow breaking
out before price does.

## Rules

- **OBV:** OBV[0] = 0; OBV[i] = OBV[i-1] + v[i] if c[i] > c[i-1],
  OBV[i-1] - v[i] if c[i] < c[i-1], unchanged if the close is equal.
- **Long entry:** OBV closes above its prior-20-bar high
  (transition only).
- **Short entry:** OBV closes below its prior-20-bar low
  (transition only).
- **Long exit:** OBV closes below its prior-20-bar low.
- **Short exit:** OBV closes above its prior-20-bar high.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 40 bars (OBV extremes need 20 bars + 1 shift).

All computation is causal: OBV uses closes/volumes through bar i
only, and the breakout levels use bars i-20..i-1.

## Sources

- Investopedia, "On-Balance Volume (OBV)":
  https://www.investopedia.com/terms/o/onbalancevolume.asp

## Files

- `indicators.py` — OBV, prior-20-bar OBV high/low, ATR(14)
- `signals.py` — transition-only entry / level exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_obv_breakout.py` — 16 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices

## How to run

From the repo root:

```
python3 -m pytest strategies/obv_breakout/test_obv_breakout.py -q
python3 strategies/obv_breakout/run_backtest.py
```

## Verdict

Loser, near breakeven: -$1,847.30 combined on 909 trades (PF 0.96,
Sharpe -0.33). All three coins red; 816 of 909 exits are harness
stops, and fees ($6,844.59) exceed the net loss. No edge on this
window — see BACKTEST.md.

Paper only, no live execution.
