# Rolling VWAP Cross — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), sliced to the batch window 2026-03-14 00:00 UTC →
2026-10-23 00:00 UTC (ms `[1773446400000, 1792713599000)`): 226
trades across the three coins.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=60 bars.

## Results (shipped config: 24-bar rolling VWAP, slope lookback 3,
cross + rising/falling slope + vol > 1.2× entry, opposite-cross
exit, 1.5xATR stop, 2xATR chandelier trail, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 86 | 33.7% | +$753 | +7.5% | +0.71 | -7.7% | +$8.75 | 1.16 |
| ETH | 89 | 21.3% | -$2,152 | -21.5% | -2.79 | -23.5% | -$24.18 | 0.52 |
| HYPE | 51 | 25.5% | -$1,529 | -15.3% | -2.46 | -17.6% | -$29.97 | 0.44 |
| **Combined** | **226** | **27.0%** | **-$2,928** | — | — | — | -$12.95 | — |

Fees: BTC $1,352, ETH $932, HYPE $313 (total $2,597).

## Verdict: a loser — the filter story fails on 1h crosses

Combined -$2,928 across 226 trades, 27% win rate, both
non-BTC legs deeply red (PF 0.52 / 0.44). BTC is marginally
green (+$753 net, PF 1.16) but net only *half* of its $1,352 in
fees — a fee-adjacent scalp, not an edge, and an isolated green
leg among three doesn't survive a multiple-comparisons squint.

The mechanics point the way to why. The entry demands a
slope-consistent, flow-backed cross — but on 1h bars the slope
filter is nearly always satisfied in any sustained move (a
24-bar VWAP tilts easily), and 1.2× volume is not a demanding
bar in crypto's bursty volume regime. So the filters pass most
crosses, and the strategy is close to a *bare* VWAP cross with a
slightly delayed entry — which is exactly the whipsaw machine
the literature warns about. The opposite-cross exit then
guarantees the loss is realized quickly: every range flicker
that triggered entry reverses out within a few bars, paying
~0.055% round-trip cost for the privilege.

The short side is the main bleeder (ETH/HYPE legs, PF 0.44–0.52):
shorting a VWAP cross-below during a 7-month net-uptrend window
fights drift, and the tight exit gives no room for the
mean-reversion leg to breathe. BTC's partial offset comes from
longs catching its trend days — a directional bet masquerading
as a benchmark trade.

Honest read: as specified this is not tradeable. If the idea is
revisited, it needs a harder participation filter (e.g., 2–3×
volume, block-volume percentile), a choppiness gate (ADXR or
donchian width so crosses only fire in trending regimes), or a
daily-scale VWAP — and any of that must be validated on
walk-forward data, not this window (see CALIBRATION.md: no
in-sample tuning was performed).

## Mechanism

24-bar rolling VWAP of typical price (zero-volume → tp
fallback), slope = vwap − vwap.shift(3), vol_ratio = v /
SMA(v,20). Long: close crosses above VWAP & slope > 0 &
vol_ratio > 1.2. Short: mirror. Exit: opposite cross. 1.5xATR
stop, 2xATR chandelier trail, 72-bar max hold. All params fixed
a priori; no optimization.

Sources: https://algotradinglib.com/en/pedia/v/vwap_cross.html —
https://bingx.com/en/learn/article/vwap-explained-what-it-is-how-traders-use-it

## Limitations

- Single 7-month crypto window; 226 trades is a thin sample for a
  filtered-cross system.
- Two of three legs deeply negative; BTC leg only fee-adjacent.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window.
