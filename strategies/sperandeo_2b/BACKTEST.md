# Sperandeo 2B False-Breakout Reversal — Backtest

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
| BTC | 26 | 30.8% | -1017.48 | -2.22 | -11.6% | -39.13 | 0.27 |
| ETH | 21 | 38.1% | 36.08 | 0.11 | -5.3% | 1.72 | 1.04 |
| HYPE | 17 | 23.5% | -540.39 | -1.51 | -7.9% | -31.79 | 0.43 |
| **Combined** | **64** | **31.2%** | **-1521.79** | **-1.68** | **-6.6%** | **-23.78** | **0.53** |

Fees: total $546.71.
Exits: BTC {'stop': 26}; ETH {'stop': 21}; HYPE {'stop': 16, 'signal': 1}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k).

Raw 2B signals fired: BTC 26 (14 long / 12 short), ETH 21 (11 / 10),
HYPE 17 (10 / 7) — every signal became a trade (one position at a
time, no signal skipped). The 10x ATR target was never hit on any
coin; the single non-stop exit was one HYPE signal exit.

## Verdict: Loser combined on paper (−$1,521.79, PF 0.53, Sharpe −1.68).

The 2B is a rare, selective pattern — 64 signals in ~8 months across
three coins — and on 1h crypto it does not pay: 63 of 64 trades die
on the 2x ATR stop, the win rate is 31.2%, and the profit factor of
0.53 means losers outweigh winners roughly two-to-one in dollar
terms. BTC is the worst (−$1,017.48, Sharpe −2.22), HYPE also loses
(−$540.39), and ETH's +$36.08 is a rounding error, not an offset.
The 10x ATR target (5x the stop distance) was never reached, so the
pattern's asymmetric-payoff premise never materialised in this
window — trades bleed out on the stop instead of running to the
target. Not a tradeable signal as shipped.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- The 2B fires rarely (64 signals), so per-coin samples (17–26
  trades) are small and the estimates are noisy.
- The harness ATR stop only approximates Sperandeo's stop above the
  false-breakout high / below the false-breakout low (see
  CALIBRATION.md).
- Never tune the shipped parameters on this window.

Paper only, no live execution.
