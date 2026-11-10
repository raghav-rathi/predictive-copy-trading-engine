# Connors Double 7s — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794315600000) (2026-03-14 22:00 UTC →
2026-11-10 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 10xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5775, ETH 5775, HYPE 5773.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 3 | 33.3% | -77.95 | -0.67 | -1.6% | -25.98 | 0.31 |
| ETH | 5 | 40.0% | -122.04 | -1.22 | -2.4% | -24.41 | 0.43 |
| HYPE | 2 | 50.0% | -31.67 | -1.03 | -1.6% | -15.83 | 0.69 |
| **Combined** | **10** | **40.0%** | **-231.67** | **-1.10** | **-1.5%** | **-23.17** | **0.46** |

Fees: total $15.50.
Exits: BTC {'signal': 2, 'stop': 1}; ETH {'signal': 3, 'stop': 2}; HYPE {'signal': 1, 'stop': 1}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

## What actually happened

The 200-day SMA warmup (4800 hourly bars) leaves only ~40 eligible
trading days (from ~2026-09-30), so the system fired just 14–16 entry
signals per coin and, one position at a time, closed only 10 trades
in total. Every coin lost money. The signal exits (6 of 10) mostly
cut small winners or scratch trades; the losers were dominated by the
stop.

The 10x ATR stop was NOT inert, contrary to the a priori expectation
in the task brief. Four of the ten exits (40%) were stops, each
costing almost exactly ~1% of equity (-$100.72 to -$102.18) — the
risk sizing guarantees that. A 10x *hourly* ATR stop is wide bar to
bar, but these positions are held for days (up to 16 days), and in
the Oct–Nov 2026 downtrend the multi-day drift from entry exceeded
10x the 1h ATR: e.g. BTC entered 2026-10-23 at $81,410 and stopped
out 2026-10-30 at $77,545; ETH entered 2026-10-08 at $2,573.30 and
stopped out the same day at $2,426.67. The original system has no
stop at all, so those four trades would have stayed open until a
7-day-high close instead; the stop is a harness formality that
changed the outcome anyway. No parameter was changed in response —
this is reported as-is.

Three positions (one per coin) were still open at the end of the
window, with combined unrealized MTM of -$156.19. The combined
realized net of -$231.67 therefore understates the mark-to-market
result: summed end equity is $29,612.14, i.e. -$387.86 on $30k.

## Verdict: Loser on paper (−$231.67 realized, PF 0.46, Sharpe −1.10).

Ten trades is far too few to condemn or vindicate the system — the
sample is essentially noise — but what little there is points the
wrong way: a 40% win rate with losers (~1% each, stop-sized) much
larger than winners, PF 0.46. Buying 7-day lows in a market that
kept making lower lows (Oct–Nov 2026) meant catching falling knives
above a 200-day SMA that was itself rolling over. The honest read is
"loser on a tiny, adverse sample in one window", not a verdict on
the system in general. Not a tradeable signal as shipped.

## Limitations

- Single ~8-month crypto window, of which only ~40 days were
  eligible after the 200-day warmup; 10 closed trades is not a
  statistically meaningful sample.
- The window's regime (a sharp Oct–Nov 2026 downtrend) is exactly
  the regime where buying short-term lows under a long-term average
  underperforms; no other regime was tested.
- Funding unmodeled; next-bar-open execution vs idealized buy-on-close.
- The 10x ATR harness stop fired on 4 of 10 exits and is not part of
  the original system — a stop-free run would give different numbers.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
