# Early Onset Trend — Backtest

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
| BTC | 133 | 34.6% | -1180.31 | -1.02 | -16.9% | -8.87 | 0.81 |
| ETH | 135 | 37.0% | -1440.28 | -1.28 | -19.3% | -10.67 | 0.78 |
| HYPE | 131 | 42.7% | 2118.70 | 1.56 | -9.5% | 16.17 | 1.38 |
| **Combined** | **399** | **38.1%** | **-501.90** | **-0.13** | **-7.8%** | **-1.26** | **0.97** |

Fees: total $3039.18.
Exits: BTC {'stop': 120, 'signal': 13}; ETH {'stop': 121, 'signal': 14}; HYPE {'stop': 111, 'signal': 20}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$29,498.10.

## Verdict: LOSER (marginal) — −$501.90 combined on 399 trades, essentially breakeven before fees, do not trade as shipped.

The closest to breakeven of this batch (PF 0.97, Sharpe −0.13,
−7.8% combined drawdown), but still negative, and the composition is
unconvincing: HYPE is a genuine winner (+$2,119, PF 1.38, Sharpe
1.56, 42.7% win rate) while BTC and ETH both lose ~$1,200–1,400 with
PF 0.78–0.81. The exit profile is the red flag — 352 of 399 trades
exit on the ATR stop and only 47 on the quotient signal, so the
zero-cross exit almost never gets to act: entries are taken, price
drifts against them, and the stop does the work. The quotient's
"early" detection is not early enough on 1h bars to beat a 2xATR
stop, and the HYPE win may be a coin-specific regime artefact (HYPE
trended strongly in this window) rather than indicator edge. At 399
trades the combined −$502 is within noise of zero, but there is no
evidence of a positive edge to trade.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- HYPE's win does not generalise on this evidence; BTC/ETH both lose.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
