# Keltner Channel Breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794488400000) (2026-03-14 22:00 UTC →
2026-11-12 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5823, ETH 5823, HYPE 5821.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | PF |
|---|---|---|---|---|---|---|---|
| BTC | 244 | 21.7% | -3207.91 | -3.44 | -32.8% | -13.15 | 0.56 |
| ETH | 244 | 22.5% | -3572.35 | -3.84 | -37.8% | -14.64 | 0.47 |
| HYPE | 274 | 21.5% | -2890.64 | -3.36 | -29.0% | -10.55 | 0.56 |
| **Combined** | **762** | **21.9%** | **-9670.91** | **-5.08** | **-33.1%** | **-12.69** | **0.53** |

Fees: total $4906.16.
Exits: BTC {'signal': 182, 'stop': 62}; ETH {'signal': 179, 'stop': 65}; HYPE {'signal': 237, 'stop': 37}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$20,329.09.

## Verdict: LOSER — -$9,670.91 on 762 trades, combined Sharpe -5.08, MaxDD -33.1%.

A bad loser on every coin (BTC -$3,207.91, ETH -$3,572.35,
HYPE -$2,890.64; PF 0.47–0.56 everywhere, win rate ~22%). The exit
split tells the story: 598 of 762 trades ended on the channel-re-entry
signal and only 164 on the stop/trail. The "exit on close back inside
the channel" rule is a hair trigger — a breakout close that fails to
hold above the band for even one bar exits immediately, so the system
churns in and out of the same breakout, paying $4,906.16 in fees on
762 trades while catching almost no follow-through. Contrast the
Wilder Volatility System (batch 33 winner, +$3,757.96): its trigger is
the previous bar's range + a full ATR, a rarer event, and its exit is
the reverse trigger, not an instant re-entry. The Keltner breakout
entry as shipped fires far too often on 1h crypto and the exit gives
winners no room to run. Not tradeable as shipped.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 762-trade sample: a large sample, but one window and all three
  coins losing the same way — the failure is structural (entry/exit
  design), not a coin-specific fluke.
- The fast re-entry exit dominates the result (598/762 signal exits);
  the reported result is really the entry + the hair-trigger exit,
  not a test of the Keltner entry in isolation.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
