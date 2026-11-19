# Mitigation Block — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795096800000) (2026-03-14 22:00 UTC →
2026-11-19 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5992, ETH 5992, HYPE 5990. (The CSVs each
contain one further bar at exactly END_MS; the half-open window
excludes it. HYPE's cache starts 2 bars into the window.)

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 130 | 31.5% | -1534.07 | -1.57 | -16.7% | -11.80 | 0.72 |
| ETH | 122 | 37.7% | 209.87 | 0.24 | -16.3% | 1.72 | 1.04 |
| HYPE | 159 | 25.2% | -2192.13 | -2.42 | -23.2% | -13.79 | 0.66 |
| **Combined** | **411** | **30.9%** | **-3516.32** | **-1.91** | **-15.4%** | **-8.56** | **0.79** |

Fees: total $3079.10.
Exits: BTC {'stop': 83, 'signal': 47}; ETH {'stop': 80, 'signal': 42}; HYPE {'stop': 92, 'signal': 67}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$26,430.82.

## Verdict: LOSER — -$3,516.32 on 411 trades, combined Sharpe -1.91, MaxDD -15.4%.

Two of three coins lose with the same shape (BTC -$1,534.07, PF
0.72; HYPE -$2,192.13, PF 0.66), and ETH's +$209.87 (PF 1.04)
is flat noise, not an offset. Win rate 30.9% combined with
expectancy -$8.56/trade: the return into a failure-swing block
does not hold as a level on 1h crypto — most entries either stop
out (255 of 411 trades end on the harness stop/trail) or exit
through the block shortly after entry. Total fees $3,079.10 are
nearly the whole net loss, so gross of fees the strategy is only
slightly negative; the edge, if any, is far too small to survive
the round-trip cost. No parameter was tuned; the spec shipped as
written.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 411 trades is a reasonable sample for a loser verdict, but it is
  still one window and three correlated coins.
- The centre-bar block definition and the wick-based
  traded-through test are interpretation choices; see
  CALIBRATION.md.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
