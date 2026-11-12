# MAMA — Backtest

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
| BTC | 251 | 30.7% | -2539.70 | -1.63 | -26.9% | -10.12 | 0.75 |
| ETH | 263 | 35.4% | 1573.70 | 0.98 | -19.6% | 5.98 | 1.13 |
| HYPE | 233 | 35.6% | 640.97 | 0.56 | -20.4% | 2.75 | 1.05 |
| **Combined** | **747** | **33.9%** | **-325.03** | **0.08** | **-15.5%** | **-0.44** | **0.99** |

Fees: total $6540.38.
Exits: BTC {'stop': 201, 'signal': 50}; ETH {'stop': 206, 'signal': 57}; HYPE {'stop': 196, 'signal': 37}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$29,931.56.

## Verdict: LOSER (marginal) — -$325.03 on 747 trades, combined Sharpe 0.08, MaxDD -15.5%.

MAMA is essentially breakeven: net −$325.03 on a $30k combined book
after $6,540.38 in fees, PF 0.99, Sharpe 0.08. Two of three coins win
(ETH +$1,573.70 at Sharpe 0.98, PF 1.13; HYPE +$640.97, PF 1.05) and
BTC loses −$2,539.70 (Sharpe −1.63), which is exactly the size of the
combined loss. The MAMA/FAMA cross is far more selective than a plain
MA cross — 747 trades versus FRAMA's 3,111 on the same window — and
the 33.9% win rate with near-unit PF means the system neither wins
nor loses convincingly: it is a coin flip that pays fees. No coin
clears a Sharpe of 1. Nothing here justifies live capital, but unlike
FRAMA it is not a structural blow-up; it is simply no edge on 1h
crypto at these settings.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 747-trade sample: a real sample, but the result sits within noise
  of breakeven — the honest read is "no edge", not "almost a winner".
- The harness stop/trail ends 603 of 747 trades; the opposite-cross
  exit fires only 144 times, so the reported result is mostly the
  MAMA/FAMA entry plus the 2xATR stop / 2.5xATR trail.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
