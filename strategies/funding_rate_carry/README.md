# Funding-Rate Carry

Directional funding carry on Hyperliquid perps: when the
24-hour average funding rate is deeply one-sided, the crowd
is paying to hold that side -- fade the crowd on price and
harvest the funding payments while you hold.

- **Long:** 24h average funding crosses BELOW -0.0000125
  (funding deeply negative: shorts pay longs, crowded
  shorts). The long is contrarian on price and *receives*
  funding while held.
- **Short:** 24h average funding crosses ABOVE +0.0000125
  (funding deeply positive: longs pay shorts, crowded
  longs). The short *receives* funding while held.
- **Long exit:** 24h average funding crosses ABOVE
  -0.00000625 (funding normalized; or the opposite entry
  fires)
- **Short exit:** 24h average funding crosses BELOW
  +0.00000625 (or the opposite entry fires)
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 168-bar
  max hold (funding accrues hourly; holds run days), 1%
  risk/trade, 3x leverage

## Threshold rule (set from the data BEFORE looking at PnL)

THRESH = 0.0000125 (0.00125% per hour) is the 90th percentile
of positive `fund_avg_24h` values pooled across BTC/ETH/HYPE
over the batch-48 window (2026-03-14 → 2026-11-27), computed
from the local funding cache before any backtest was run.
The negative-side 90th percentile of |`fund_avg_24h`| is
0.00001252, essentially identical, so the symmetric
threshold is consistent with the data on both sides. The
exit level is THRESH/2 = 0.00000625. Per-coin distribution
(24h-average funding over the window):

| Coin | Mean | Median | % positive | p90 of positives | Min | Max |
|---|---|---|---|---|---|---|
| BTC | 0.000007 | 0.000009 | 85.3% | 0.0000125 | -0.000019 | 0.000021 |
| ETH | 0.000007 | 0.000009 | 85.7% | 0.0000125 | -0.000024 | 0.000019 |
| HYPE | 0.000011 | 0.000011 | 96.1% | 0.0000162 | -0.000010 | 0.000064 |

Two consequences worth knowing before reading BACKTEST.md:
funding is positive most of the time on all three coins, so
short entries (crowded longs) fire far more often than long
entries; and HYPE's 24h-average funding never drops below
-0.000010, so HYPE can NEVER trigger a long entry at the
shipped threshold -- its 24 trades are all shorts. That is a
property of the data, not a bug, and the threshold was not
lowered to force HYPE longs.

## Funding economics

Hyperliquid funding is paid hourly: a positive rate means
longs pay shorts, a negative rate means shorts pay longs.
The harness runs with `use_funding=False`, so its net PnL is
price-only; `run_backtest.py` additionally computes funding
PnL per trade from the LOCAL cache (`data/funding/{COIN}_1h.csv`,
the same rows the indicators merge): notional = entry price
x quantity, rates = hourly funding rates with t in
[entry_t, exit_t), funding = `funding_pnl_usd(side, notional,
rates)` from `strategies.backtest`. TOTAL = price PnL +
funding PnL is the headline; the price-only number is always
shown alongside. See BACKTEST.md for the accounting method.

Entries are CROSS-based, never level conditions: a cross
fires once, so the strategy cannot re-enter every bar while
funding stays extreme. The funding series is merged 1:1 onto
the candle grid on `t`; a missing cache file or a missing
funding row raises a clear ValueError (never silently filled
or substituted).

Sources: Hyperliquid funding mechanics (positive rate =
longs pay shorts; see `paper/STRATEGY_RESEARCH.md` §3) and
https://swolecharts.com/hyperliquid/funding-rate

Usage:

```python
from strategies.funding_rate_carry import indicators, signals, risk

df.attrs["coin"] = "BTC"  # set by the driver
df = indicators.add_indicators(df)
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-27 Hyperliquid
1h (BTC/ETH/HYPE, batch-48 pinned window) results and
CALIBRATION.md for the threshold sensitivity check.
