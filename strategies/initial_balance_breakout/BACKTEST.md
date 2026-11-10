# Initial Balance Breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794315600000) (2026-03-14 22:00 UTC →
2026-11-10 13:00 UTC), duplicates dropped (keep first). $10k start per coin, 1%
risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off.

**Bar counts used:** BTC 5775, ETH 5775, HYPE 5773.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 238 | 36.6% | -2601.91 | -4.70 | -26.6% | -10.93 | 0.53 |
| ETH | 237 | 37.6% | -1091.89 | -1.78 | -11.8% | -4.61 | 0.77 |
| HYPE | 237 | 40.1% | -1911.70 | -3.47 | -20.1% | -8.07 | 0.64 |
| **Combined** | **712** | **38.1%** | **-5605.50** | **-4.53** | **-19.1%** | **-7.87** | **0.64** |

Fees: total $5260.20.
Exits: BTC {'signal': 217, 'stop': 21}; ETH {'signal': 222, 'stop': 15}; HYPE {'signal': 216, 'stop': 21}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$24,394.50.

## Verdict: Loser combined on paper (−$5,605.50, PF 0.64, Sharpe −4.53).

The Initial Balance breakout loses on all three coins. It fires ~one trade per day (712 trades over ~241 days) and the overwhelming majority die on the signal exit — 655 of 712 exits are signal exits, i.e. the breakout is reclaimed (close back inside the IB) or, less often, the 1x extension target is hit and the trade still nets a loss after the round-trip costs — while only 57 hit the ATR stop. Win rates of 36.6–40.1% with profit factors of 0.53–0.77 mean losers outweigh winners by a wide margin even before fees; after $5,260.20 of fees the combined curve falls −19.1% peak-to-trough to $24,394.50. The first-hour range of a 24/7 crypto day simply does not carry the directional information the CBOT session-open range did: breaks of the first hour's high/low are reclaimed within the day far more often than they extend to the 1x target. Not a tradeable signal as shipped.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- The 1h first bar is a coarse Initial Balance: the book's IB is the
  first 30–60 minutes of a pit session with a real open/close, while
  crypto trades 24/7 and the 00:00 UTC "open" is arbitrary.
- Signal exits are evaluated against the current day's IB; a position
  carried past midnight exits against the new day's IB (see
  CALIBRATION.md).
- Never tune the shipped parameters on this window.

Paper only, no live execution.
