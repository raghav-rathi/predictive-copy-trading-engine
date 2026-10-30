# Money Flow Index — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), read directly —
`fetch_candles` was NOT called, so the cache was not
rewritten. Window t in [1773525600000, 1793318400000]
(2026-03-14 22:00 UTC → 2026-10-30 00:00 UTC), duplicate t
dropped (keep first). $10k start per coin, 1% risk per trade
on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP=20 bars.

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

## Results (shipped config: MFI(14) 20/80 recovery/fade
entries, 50-midline exits, 2xATR stop, 2.5xATR trail,
120-bar max hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 126 | 42.9% | -$1,159.45 | -1.12 | -16.70% | -$9.20 | 0.78 |
| ETH | 135 | 40.7% | -$1,157.75 | -1.11 | -22.16% | -$8.58 | 0.80 |
| HYPE | 121 | 33.1% | -$1,308.88 | -1.29 | -20.06% | -$10.82 | 0.77 |
| **Combined** | **382** | **39.0%** | **-$3,626.08** | -1.92 | -14.57% | **-$9.49** | — |

Fees: BTC $1,231.26, ETH $1,012.70, HYPE $588.19 (total
$2,832.16). Long/short split: BTC 59/67, ETH 70/65, HYPE
51/70 — roughly symmetric. Exits: 276 stop / 106 signal /
0 max-hold.

## Verdict: loser, do not trade as shipped

−$3,626 across 382 trades on $30k capital, losing on all
three coins with per-coin profit factors of 0.77–0.80. The
win rate (39.0%) flatters the strategy: winners are smaller
than losers, and the 2xATR stop catches most trades before
the midline exit can manage them.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- Volume is single-venue (Hyperliquid) base-asset volume,
  not whole-market dollar volume; MFI's "money flow" reading
  is correspondingly narrower than on equities.
- Never tune the shipped parameters on this window.
