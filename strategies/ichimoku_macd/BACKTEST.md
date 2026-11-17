# Ichimoku MACD — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794924000000) (2026-03-14 22:00 UTC →
2026-11-17 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5944, ETH 5944, HYPE 5942.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 97 | 30.9% | -327.34 | -0.23 | -12.3% | -3.37 | 0.92 |
| ETH | 102 | 25.5% | -862.53 | -0.76 | -13.4% | -8.46 | 0.81 |
| HYPE | 94 | 38.3% | 936.21 | 0.91 | -13.3% | 9.96 | 1.22 |
| **Combined** | **293** | **31.4%** | **-253.65** | **-0.06** | **-10.3%** | **-0.87** | **0.98** |

Fees: total $2427.68.
Exits: BTC {'stop': 71, 'signal': 26}; ETH {'stop': 75, 'signal': 27}; HYPE {'stop': 68, 'signal': 26}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$29,732.28.

## Verdict: LOSER (near breakeven) — -$253.65 on 293 trades, combined Sharpe -0.06, MaxDD -10.3%.

Ichimoku + MACD is the closest to breakeven of this batch but
still a loser: HYPE is a genuine winner (+$936.21, PF 1.22,
Sharpe 0.91, expectancy +$9.96/trade) while BTC (-$327.34,
PF 0.92) and ETH (-$862.53, PF 0.81, win rate 25.5%) lose, and
the combined PF of 0.98 does not clear $2,427.68 in fees. The
three-way filter (cloud + Tenkan/Kijun cross + histogram sign)
keeps the trade count low (293, the most selective of the batch)
and the drawdowns contained (combined MaxDD -10.3%, the mildest
of the batch), and the signal exits actually fire here (79 of
293 trades, ~27%, vs 7% for Supertrend-RSI) — the cloud-entry
exit does real work. But selectivity without edge is just fewer
losing trades: win rates of 26–38% with a 2xATR stop mean the
system needs a much higher payoff per win than it gets. One-coin
positive (HYPE) against two-coin negative is not a tradeable
edge.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 293-trade sample; the HYPE win (+$936.21) is the only positive
  coin and may be noise — BTC/ETH both lose.
- The displaced-cloud reading (spans as plotted at bar i) is a
  documented spec choice; the unshifted-cloud variant was not
  tested and is not claimed to be better or worse.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
