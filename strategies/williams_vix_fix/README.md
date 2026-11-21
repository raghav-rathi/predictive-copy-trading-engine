# Williams VIX Fix

Larry Williams' VIX Fix (Active Trader, December 2007): a fear-spike
detector built from closes and lows. When the market prints a sharp
downward spike, WVF jumps above its band — the "green flash" — and
this strategy buys that flash (and symmetrically shorts the inverted
flash on upside spikes).

## Rules

- **WVF:** 100 x (highest close over 22 bars - low) / highest close
  over 22 bars.
- **Upper band:** SMA(20) of WVF + 2.0 x std(20) of WVF.
- **Range high:** 0.85 x max WVF over the trailing 50 bars.
- **Green flash:** WVF >= upper band OR WVF >= range high.
- **Inverted WVF:** 100 x (high - lowest close over 22 bars) /
  lowest close over 22 bars, with its own upper band and range high
  computed the same way.
- **Long entry:** green flash on this bar AND NOT on the previous
  bar (transition only).
- **Short entry:** inverted flash on this bar AND NOT on the previous
  bar (transition only).
- **Long exit:** inverted flash (any bar).
- **Short exit:** green flash (any bar).
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.
- Warmup 70 bars (range high is first defined at bar 70).

All computation is causal: rolling windows are trailing, and the
flash state uses bars through the current close only.

## Sources

- Larry Williams, "The VIX Fix" (Active Trader, Dec 2007), original
  article PDF: https://c.mql5.com/forextsd/forum/77/fix_the_vix.pdf
- StockSharp API example, "Williams VIX Fix":
  https://doc.stocksharp.com/en/api-examples/0454_Williams_Vix_Fix

## Files

- `indicators.py` — WVF, inverted WVF, bands, range highs, flash flags
- `signals.py` — flash-transition entry/exit booleans
- `risk.py` — batch-standard RiskConfig + WARMUP
- `test_williams_vix_fix.py` — 16 unit tests, synthetic data only
- `run_backtest.py` — local-cache backtest runner
- `BACKTEST.md` — shipped backtest results
- `CALIBRATION.md` — parameter choices

## How to run

From the repo root:

```
python3 -m pytest strategies/williams_vix_fix/test_williams_vix_fix.py -q
python3 strategies/williams_vix_fix/run_backtest.py
```

## Verdict

Loser: -$8,283.67 combined on 1313 trades (PF 0.83, Sharpe -2.22,
MaxDD -33.8%). All three coins lose; gross PnL before fees is about
-$210, so the entries are breakeven before costs and the $8,074 of
fees does the killing. No edge on this window — see BACKTEST.md.

Paper only, no live execution.
