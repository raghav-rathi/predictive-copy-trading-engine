# Price Channel Breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794488400000) (2026-03-14 22:00 UTC →
2026-11-12 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5823, ETH 5823, HYPE 5821.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 168 | 33.3% | -1294.40 | -0.89 | -19.6% | -7.70 | 0.83 |
| ETH | 166 | 34.3% | -579.58 | -0.31 | -20.2% | -3.49 | 0.92 |
| HYPE | 181 | 32.6% | -1417.94 | -0.95 | -19.4% | -7.83 | 0.84 |
| **Combined** | **515** | **33.4%** | **-3291.91** | **-1.03** | **-15.1%** | **-6.39** | **0.86** |

Fees: total $3868.71.
Exits: BTC {'stop': 156, 'signal': 12}; ETH {'stop': 153, 'signal': 13}; HYPE {'stop': 172, 'signal': 9}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$26,712.67 (vs $30,000 + net −$3,291.91 = $26,708.09; the $4.58 gap is
the mark-to-market of a position still open at the window end).

## Verdict: LOSER — −$3,291.91 on 515 trades, combined Sharpe −1.03, MaxDD −15.1%.

The 30-bar channel breakout loses on all three coins (BTC −$1,294.40,
ETH −$579.58, HYPE −$1,417.94; every PF below 1.0). Win rate 33.4% with
PF 0.86 means the winners do not outrun the losers, and $3,868.71 in
fees on 515 trades eats what little the winners bank. The exit split
is the tell: 481 of 515 trades ended on the harness stop/trail and
only 34 on the midline cross, so the shipped system is effectively a
channel-breakout entry plus the 2xATR stop / 2.5xATR trail — the
midline exit almost never gets the chance to fire, and on 1h crypto
the 30-bar breakout is a whipsaw entry: price makes a new 30-bar
extreme, then mean-reverts into the stop. Same failure mode as the
Donchian systems in earlier batches — breakout entries without a
trend filter do not survive 1h crypto chop.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 515-trade sample: a real sample, and the loss is consistent across
  all three coins, so this is not a one-coin artifact.
- The midline exit almost never fires (34/515); the reported result
  is really the entry + harness stop/trail, not the full system as
  written.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
