# DMI Cross — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), read directly —
`fetch_candles` was NOT called, so the cache was not
rewritten. Window t in [1773525600000, 1793318400000]
(2026-03-14 22:00 UTC → 2026-10-30 00:00 UTC), duplicate t
dropped (keep first). $10k start per coin, 1% risk per trade
on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP=40 bars.

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

## Results (shipped config: DI cross, ADX(14) > 20 entry gate,
opposite-cross exit, 2xATR stop, 2.5xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 190 | 22.6% | -$3,129.23 | -2.83 | -32.98% | -$16.47 | 0.57 |
| ETH | 168 | 28.0% | -$1,190.31 | -1.11 | -19.20% | -$7.09 | 0.81 |
| HYPE | 194 | 27.3% | -$389.07 | -0.22 | -12.16% | -$2.01 | 0.94 |
| **Combined** | **552** | **25.9%** | **-$4,708.61** | -2.19 | -17.17% | **-$8.53** | — |

Fees: BTC $1,656.40, ETH $1,505.28, HYPE $908.76 (total
$4,070.43). Long/short split: BTC 94/96, ETH 84/84, HYPE
98/96 — symmetric, no directional bias to blame. Exits:
303 stop / 249 signal / 0 max-hold.

## Verdict: loser, do not trade as shipped

−$4,709 across 552 trades on $30k starting capital, losing
on all three coins, with a 25.9% win rate and a −2.19
combined Sharpe. The DI cross fires often (552 trades) and
is usually wrong within the 2xATR stop's reach; the ADX > 20
gate filters chop only weakly. HYPE's near-breakeven
(−$389, PF 0.94) is the best of a bad set, not an edge.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- ADX is a double-smoothed lagging indicator: by the time
  ADX > 20 confirms a trend, the DI cross that triggered
  the trade is often already reversing.
- Never tune the shipped parameters on this window.
