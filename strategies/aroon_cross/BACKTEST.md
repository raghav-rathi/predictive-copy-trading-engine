# Aroon Cross — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), read directly —
`fetch_candles` was NOT called, so the cache was not
rewritten. Window t in [1773525600000, 1793318400000]
(2026-03-14 22:00 UTC → 2026-10-30 00:00 UTC), duplicate t
dropped (keep first). $10k start per coin, 1% risk per trade
on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP=30 bars.

**Bar counts (match the brief's expected counts exactly):**
BTC 5499, ETH 5499, HYPE 5497. Reconciliation per file:
5 exact-duplicate rows dropped, plus 1 row after the window
end (t=1793322000000, 2026-10-30 01:00 UTC) excluded by the
filter — e.g. BTC 5505 − 5 − 1 = 5499. BTC/ETH first bar
1773525600000 (2026-03-14 22:00 UTC); HYPE first bar
1773532800000 (2026-03-15 00:00 UTC, 2 hours later); all
coins last bar 1793318400000 (2026-10-30 00:00 UTC).

**Method note:** run through `strategies/backtest.py`
`run_backtest` with this strategy's own RiskConfig, via a
throwaway runner in /tmp (not in the worktree). Combined
Sharpe / MaxDD are computed on the summed $30k three-coin
equity curve (positionally aligned, truncated to the
shortest series).

## Results (shipped config: Aroon(25) cross, > 70 gate on the
crossing line, opposite-cross exit, 2xATR stop, 2.5xATR
trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 204 | 35.8% | -$1,675.73 | -1.13 | -22.62% | -$8.21 | 0.80 |
| ETH | 186 | 36.6% | +$923.02 | +0.74 | -16.37% | +$4.96 | 1.10 |
| HYPE | 198 | 37.9% | +$871.73 | +0.68 | -10.05% | +$4.40 | 1.09 |
| **Combined** | **588** | **36.7%** | **+$119.03** | +0.11 | -10.53% | **+$0.20** | — |

Fees: BTC $2,287.80, ETH $1,823.99, HYPE $1,081.29 (total
$5,193.08). Long/short split: BTC 104/100, ETH 93/93, HYPE
97/101 — symmetric. Exits: 516 stop / 72 signal /
0 max-hold.

## Verdict: no demonstrated edge (flat, not a win)

+$119 over 588 trades on $30k capital is 0.4% over ~7.5
months — noise, and it survives only because ETH and HYPE
gains barely offset the BTC loss. The stop, not the
opposite cross, manages 88% of trades, which says the
cross's follow-through is weak at this horizon.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- Aroon is time-based only: it cannot tell a marginal new
  high from a decisive breakout, so strong-gate crosses
  still fire into shallow new extremes.
- Never tune the shipped parameters on this window.
