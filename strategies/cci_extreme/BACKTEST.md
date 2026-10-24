# CCI Extreme — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), FULL cached range, no slicing: BTC 5,335 bars and ETH
5,335 bars from 2026-03-14 22:00 UTC, HYPE 5,333 bars from
2026-03-15 00:00 UTC, all to 2026-10-22 23:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2.0xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=50 bars.

## Results (shipped config: CCI(20) cross back through ±100,
zero-line exit in the adverse direction, 2.0xATR stop, 2.5xATR
chandelier trail, 96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 294 | 31.3% | -$4,357 | -41.5% | -3.55 | -47.0% | -$14.82 | 0.57 |
| ETH | 289 | 37.7% | -$422 | -1.4% | +0.04 | -16.9% | -$1.46 | 0.96 |
| HYPE | 289 | 38.1% | -$987 | -7.9% | -0.47 | -19.4% | -$3.41 | 0.91 |
| **Combined** | **872** | **35.7%** | **-$5,766** | — | — | — | -$6.61 | — |

Fees: BTC $2,407, ETH $2,534, HYPE $1,331 (total $6,272).
Net % is the harness equity-curve return per leg; combined
net $ is the sum of per-leg trade PnL.

## Verdict: a loser overall, but the least-bad of this batch

Combined -$5,766 across 872 trades, 35.7% win rate, profit
factor below 1.0 on every leg — but the shape differs from the
other two batch-15 strategies. ETH is nearly flat (-$422, PF
0.96, Sharpe +0.04) and HYPE is only mildly red (-$987, PF
0.91); the damage is concentrated in BTC (-$4,357, PF 0.57,
max drawdown -47.0%). The return-through-the-level entry does
avoid the worst falling-knife trades — that is why ETH/HYPE
survive near breakeven while the batch's stochastic system
loses ~48% on the same coins — but "near breakeven before
further costs" is still not an edge, and the BTC leg shows
what happens when the stretch keeps extending: in a trending
market CCI crosses back through ±100 repeatedly as price
pauses, and each pause-cross is a counter-trend entry into a
trend that resumes.

The zero-line exit also caps winners structurally: a trade
that mean-reverts to CCI = 0 exits exactly when the move is
complete, so the average win is small while the average loss
(the stretch that extends to the 2.0xATR stop or the 96-bar
max hold) is large — the expectancy math (35.7% win rate,
PF < 1) follows directly.

Honest read: as specified this is not tradeable, but it is
the closest of the three to a workable idea. If revisited, the
fix is a trend filter on entries (take CCI extremes only
against the dominant trend's counter-move, or only when a
longer CCI confirms the stretch) — and any of that must be
validated on walk-forward data, not this window (see
CALIBRATION.md: no in-sample tuning was performed).

## Mechanism

CCI(20) = (tp − SMA(tp,20)) / (0.015 × mean deviation), tp =
(h+l+c)/3, mean deviation over the same 20 bars. Long: CCI
crosses above −100 from below; short: crosses below +100
from above. Exit: CCI crosses 0 in the adverse direction.
2.0xATR stop, 2.5xATR chandelier trail, 96-bar max hold. All
params fixed a priori; no optimization.

Sources: https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:commodity_channel_index

## Limitations

- Single 7-month crypto window; all three legs negative (ETH
  only marginally so).
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window.
