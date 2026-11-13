# Grid Trading — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794574800000) (2026-03-14 22:00 UTC →
2026-11-13 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5847, ETH 5847, HYPE 5845.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 333 | 24.6% | -7152.48 | -5.77 | -71.8% | -21.48 | 0.45 |
| ETH | 283 | 26.1% | -7031.35 | -5.67 | -71.2% | -24.85 | 0.45 |
| HYPE | 347 | 25.1% | -7237.75 | -6.20 | -72.8% | -20.86 | 0.45 |
| **Combined** | **963** | **25.2%** | **-21421.58** | **-7.73** | **-71.5%** | **-22.24** | **0.45** |

Fees: total $4149.45.
Exits: BTC {'stop': 305, 'signal': 28}; ETH {'stop': 259, 'signal': 24}; HYPE {'stop': 324, 'signal': 23}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$8,657.08.

## Verdict: LOSER — -$21,421.58 on 963 trades, combined Sharpe -7.73, MaxDD -71.5%.

The worst result in the batch series by a wide margin, and it fails
the same way on all three coins (PF 0.45 on BTC, ETH and HYPE
alike — no coin disagrees). This is the textbook grid-trading
failure mode, not a bug: the window trends hard, so buying the dip
of the range means buying into a falling market and shorting the
top means shorting into a rising one. 888 of 963 trades ended on
the harness stop and only 75 on the midpoint signal exit — price
almost never came back to the midpoint before the 2xATR stop was
hit, and the level-entry rule re-entered the same losing zone
immediately after each stop, compounding the bleed. Win rate 25.2%
with expectancy -$22.24 per trade on 963 trades is a systematic
loss, and the combined curve lost 71.5% peak-to-trough. A true
multi-level grid would have fared no better in direction — it
would have accumulated the same losing positions — it would just
have lost the money in smaller, more numerous pieces.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 963-trade sample: a large sample, and the loss is uniform across
  all three coins, so this is not a small-sample fluke.
- Single-position harness approximation (see CALIBRATION.md): the
  shipped system is one round trip per zone visit, not per-level
  grid scalps. The approximation changes trade sizing, not the
  direction of the result — the stop-dominated exit split shows
  the range kept breaking against the position either way.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
