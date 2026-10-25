# Swing Support / Resistance Bounce — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), FULL cached range: BTC/ETH 5,379 bars, 2026-03-14 22:00 UTC →
2026-10-25 00:00 UTC; HYPE 5,377 bars, 2026-03-15 00:00 UTC →
2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=100 bars.

## Results (shipped config: 250-bar lookback, 0.5% clusters, 2+
touches, 0.3% touch tolerance, 0.5% failure distance, 1.5xATR stop,
2xATR trail, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 1,209 | 27.1% | -$9,373 | -93.7% | -11.41 | -93.7% | -$7.75 | 0.46 |
| ETH | 1,122 | 27.5% | -$8,179 | -81.8% | -6.88 | -82.3% | -$7.29 | 0.59 |
| HYPE | 980 | 28.0% | -$7,813 | -78.1% | -7.35 | -78.4% | -$7.97 | 0.59 |
| **Combined** | **3,311** | — | **-$25,365** | — | — | — | -$7.66 | — |

Fees: BTC $5,714, ETH $6,122, HYPE $3,581 (total $15,417).
Exits: 2,224 signal / 1,087 stop — the signal (failure) exit fires
most of the time, which is the mechanism failing in plain sight:
price touches a "level," closes back over it (the bounce entry
triggers), then closes 0.5% beyond it (the failure exit). The
bounce is usually a pause inside a break, not a turn.

## Verdict: the batch's second disaster — a structural failure, like
classic_pivots

-$25,365 across 3,311 trades, with drawdowns of 78–94% on every
coin. It loses before fees too (BTC gross -$3,659 after removing
$5,714 of fees). The mechanism is the problem, in the same way as
classic_pivots: a "level" from two touches on noisy 1h data is
barely a level, so it gets touched constantly (~1,100 trades per
coin) and breaks more often than it holds. Raising the touch
requirement (3+ touches, tighter clusters) would be a different
strategy, not a tune — and on this evidence the prior for it working
is low. Do not trade this. Do not tune this.

## Mechanism

250-bar lookback, 0.5% clusters, 2+ touches, 0.3% touch tolerance,
0.5% failure distance, 1.5xATR stop, 2xATR trail, 72-bar max hold.
All params fixed a priori; no optimization.

Source: support / resistance bounce (Murphy, Technical Analysis of
the Financial Markets).

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window — the failure is
  structural, and tuning it would be overfitting a broken premise.
