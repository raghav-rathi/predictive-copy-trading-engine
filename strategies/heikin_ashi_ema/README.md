# Heikin Ashi EMA

Heikin Ashi candles smooth price action; this strategy trades in
the direction of the Heikin Ashi candle when the EMA trend filter
agrees, and exits when the candle flips or the fast EMA crosses
back.

## Rules

- **Heikin Ashi close:** (open + high + low + close) / 4.
- **Heikin Ashi open:** (previous HA open + previous HA close) / 2,
  seeded with (open + close) / 2 on bar 0.
- **Long entry:** bullish HA candle (HA close > HA open) AND
  EMA(9) > EMA(21) AND close > EMA(50).
- **Short entry:** bearish HA candle (HA close < HA open) AND
  EMA(9) < EMA(21) AND close < EMA(50).
- **Long exit:** HA candle flips bearish OR EMA(9) crosses below
  EMA(21).
- **Short exit:** HA candle flips bullish OR EMA(9) crosses above
  EMA(21).
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 60 bars.

Note the entry is a *state* condition as specified, not a
transition: every qualifying bar signals entry, so the strategy
re-enters immediately after an exit while the condition persists.
All computation is causal: HA open recurses forward only, and the
EMAs are trailing.

## Sources

- Heikin Ashi candles:
  https://en.wikipedia.org/wiki/Heikin_Ashi

## Files

- `indicators.py` — Heikin Ashi candles + EMA(9/21/50)
- `signals.py` — state entry / flip-or-cross exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_heikin_ashi_ema.py` — 19 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices

## How to run

From the repo root:

```
python3 -m pytest strategies/heikin_ashi_ema/test_heikin_ashi_ema.py -q
python3 strategies/heikin_ashi_ema/run_backtest.py
```

## Verdict

Heavy loser: -$24,287.26 combined on 2,895 trades (PF 0.51,
Sharpe -9.82, MaxDD -81.0%). The state entry + HA-flip exit
churns ~1 trade per 6 bars per coin. See BACKTEST.md.

Paper only, no live execution.
