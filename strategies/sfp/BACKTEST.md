# Swing Failure Pattern (SFP) — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795010400000) (2026-03-14 22:00 UTC →
2026-11-18 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5968, ETH 5968, HYPE 5966.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 196 | 27.6% | -2830.08 | -2.63 | -31.5% | -14.44 | 0.66 |
| ETH | 230 | 30.9% | -3511.69 | -3.31 | -37.3% | -15.27 | 0.59 |
| HYPE | 191 | 27.7% | -2227.07 | -2.31 | -25.2% | -11.66 | 0.69 |
| **Combined** | **617** | **28.8%** | **-8568.84** | **-4.46** | **-28.8%** | **-13.89** | **0.64** |

Fees: total $4316.59.
Exits: BTC {'signal': 101, 'stop': 95}; ETH {'signal': 125, 'stop': 105}; HYPE {'signal': 99, 'stop': 92}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$21,495.87 — $64.71 above $30,000 + combined net (-$8,568.84) because
a position was still open at the window end (mark-to-market).

## Verdict: LOSER — -$8,568.84 on 617 trades, combined Sharpe -4.46, MaxDD -28.8%.

The Swing Failure Pattern is the worst loser of batch 39 by a wide
margin: 617 trades, a 28.8% win rate, PF 0.64, and -$8,568.84 net
after $4,316.59 in fees. No coin wins — ETH is the worst (-$3,511.69,
Sharpe -3.31, MaxDD -37.3%), BTC loses -$2,830.08 and HYPE
-$2,227.07. The exit split (325 signal vs 292 stop) shows the
re-failure exit fires constantly: after a sweep-and-reclaim the
price usually keeps going through the swept level rather than
reversing, so the "trapped breakout trader" reversal does not
materialize on 1h crypto — the sweep is continuation, not failure.
No parameter was tuned; the spec shipped as written and lost badly.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 617 trades is a large sample and the loss is present on all
  three coins with Sharpe below -2.3 everywhere — the edge is
  absent, not merely unlucky.
- The volume-spike SMA includes the current bar's volume (see
  CALIBRATION.md); the literal reading was shipped, not tuned.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
