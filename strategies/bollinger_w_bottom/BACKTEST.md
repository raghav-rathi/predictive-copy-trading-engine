# Bollinger W-Bottom / M-Top — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794402000000) (2026-03-14 22:00 UTC →
2026-11-11 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5776, ETH 5776, HYPE 5774.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 158 | 23.4% | -2386.70 | -2.57 | -29.7% | -15.11 | 0.61 |
| ETH | 136 | 32.4% | -638.15 | -0.55 | -13.3% | -4.69 | 0.87 |
| HYPE | 125 | 31.2% | 2281.94 | 1.93 | -7.2% | 18.26 | 1.50 |
| **Combined** | **419** | **28.6%** | **-742.92** | **-0.29** | **-9.6%** | **-1.77** | **0.95** |

Fees: total $3775.66.
Exits: BTC {'signal': 83, 'stop': 75}; ETH {'signal': 76, 'stop': 60}; HYPE {'signal': 72, 'stop': 53}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$29,257.08.

## Verdict: Loser — −$742.92 on 419 trades, PF 0.95; the mechanized pattern fires far too often to be Bollinger's W.

The combined loss is modest, but the per-coin read is bad: BTC
−$2,387 (23.4% win, PF 0.61, Sharpe −2.57) and ETH −$638 (PF 0.87)
both lose, with HYPE's +$2,282 again the lone winner — the same
single-coin trend artefact as the rest of batch 33. The deeper
problem is frequency: 419 "W-bottoms / M-tops" in ~8 months is
roughly one per 41 bars per coin, far more often than a genuine
double-bottom pattern occurs. As mechanized — any %B < 0 bar, any
rally to the mid-band, any retest within 1% with a higher %B — the
pattern catches ordinary hourly chop, not panic-plus-retest
structure; the 28.6% combined win rate says most "confirmations"
reverse straight back through the middle band (231 of 419 exits are
the signal exit). The exit rule itself works as designed; the entry
pattern as specified is too permissive on 1h bars. Bollinger's
discretionary version (close above the intervening high, swing-low
confirmation) is stricter than what the spec mechanized.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Pattern frequency (~1 per 41 bars) shows the mechanical
  translation is looser than the discretionary original; results
  speak to this mechanization, not to Bollinger's pattern as a
  chart reader would apply it.
- HYPE's in-window trend flatters the combined figure; per-coin
  results are the honest read.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
