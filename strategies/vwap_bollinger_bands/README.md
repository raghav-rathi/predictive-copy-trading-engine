# VWAP Bollinger Bands

Session-anchored VWAP with Bollinger-style bands: fade the extremes
in a ranging market — buy when price stretches below VWAP − 2 SD,
sell when it stretches above VWAP + 2 SD — and exit when price
comes back to VWAP.

## Rules

- **Session anchor:** each UTC calendar day, reset 00:00 UTC.
  VWAP = cumulative sum(tp * v) / sum(v) since the session start,
  tp = (h + l + c) / 3.
- **Bands:** VWAP +/- 2.0 volume-weighted SD, where SD is the
  volume-weighted std of (tp − VWAP) since the session start
  (computed from cumulative sums, causal).
- **Regime filter:** only trade while ADX(14) < 25 (no strong trend).
- **Long entry:** close below the lower band AND ADX < 25.
- **Short entry:** close above the upper band AND ADX < 25.
- **Long exit:** close back at/through VWAP.
- **Short exit:** close back at/through VWAP.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 40 bars.

**Honest caveat:** crypto trades 24/7, so there is no true session
open or overnight gap — the UTC-day anchor is an adaptation, not a
market open. Early in each UTC day the bands are computed from very
few bars and are correspondingly tight/noisy; the backtest includes
that noise as shipped.

## Sources

- Tarrow Futures, "VWAP Mean Reversion Strategy":
  https://www.tarrowfutures.com/blog/vwap-mean-reversion-strategy/
- Prop Ledger, "Trading Against VWAP Bands in Ranging Regimes":
  https://prop-ledger.org/learn/paper/strategy-mean-reversion-trading-against-vwap-bands-in-ranging-regimes

## Verdict: LOSER (worst of batch 41)

Backtest (2026-03-14 → 2026-11-20, BTC/ETH/HYPE 1h, $10k per coin):
combined **-$11,712.13 on 1,078 trades, PF 0.60, Sharpe -5.81,
MaxDD -40.3%** — all three coins lose ~$3,650–$4,050 each. The win
rate is 52.3% and most trades exit at VWAP as designed, but the
wins are small and the losses are big (PF 0.60): fading 2-SD bands
on 1h crypto catches small reversions and rides the trends that
don't revert. See BACKTEST.md for the full table.

## Files

- `indicators.py` — session VWAP, volume-weighted SD bands, ADX, ATR
- `signals.py` — entry/exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_vwap_bollinger_bands.py` — 20 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices + sweep

## How to run

From the repo root:

```
python3 -m pytest strategies/vwap_bollinger_bands/test_vwap_bollinger_bands.py -q
python3 strategies/vwap_bollinger_bands/run_backtest.py
```

Paper only, no live execution.
