# RSI Hidden Divergence — Backtest

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
| BTC | 172 | 26.2% | -2466.18 | -2.27 | -28.3% | -14.34 | 0.65 |
| ETH | 170 | 30.0% | -899.39 | -0.72 | -19.1% | -5.29 | 0.86 |
| HYPE | 155 | 23.9% | -2561.86 | -2.94 | -27.9% | -16.53 | 0.53 |
| **Combined** | **497** | **26.8%** | **-5927.42** | **-2.82** | **-22.2%** | **-11.93** | **0.69** |

Fees: total $3784.07.
Exits: BTC {'stop': 99, 'signal': 73}; ETH {'stop': 95, 'signal': 75}; HYPE {'stop': 86, 'signal': 69}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$24,072.58.

## Verdict: LOSER — -$5,927.42 on 497 trades, combined Sharpe -2.82, MaxDD -22.2%.

Hidden divergence is the worst strategy of this batch by every
measure: all three coins lose (BTC -$2,466.18, ETH -$899.39, HYPE
-$2,561.86), the combined win rate is 26.8% with PF 0.69, and the
combined Sharpe of -2.82 is the deepest negative in the batch. The
signal exit does fire as designed (217 of 497 exits on the RSI-50
cross), so the result really is the divergence system, not just the
harness stop/trail — and the divergence system loses on its own
terms. The honest read: on 1h crypto, a "higher low in price, lower
low in RSI" is usually just a weak bounce inside a down move rather
than a continuation signal, and the two-bar confirmation lag means
the entry arrives after the bounce has already spent itself. The
RSI-50 exit then cuts the trade before any continuation can pay.
Nothing in the numbers suggests a small parameter tweak rescues it;
the setup itself does not carry on this timeframe.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 497-trade sample: a real sample, and the loss is consistent across
  all three coins, so it is not a one-coin artefact.
- The two-bar confirmation lag is structural to the centred-pivot
  definition; a one-sided (trailing-only) pivot would fire earlier
  but is a different setup.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
