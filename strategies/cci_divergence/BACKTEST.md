# CCI Divergence — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), window 2026-03-14 →
2026-10-27, $10k start, 1% risk per trade on the 2xATR stop, 3x
leverage cap, 0.045% fee + 0.01% slippage per side, funding off.
WARMUP=40 bars. Bars: 5,443 per coin (filtered t >=
1773525600000).

## Results (shipped config: CCI(20) pivot divergence within 40
bars, 3-bar-high/low confirmation within 20 bars, 2xATR stop,
2.5xATR trail, 168-bar max hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 55 | 29.1% | -$1,908 | -3.09 | -20.8% | -$34.68 | 0.39 |
| ETH | 43 | 34.9% | +$458 | +0.58 | -8.8% | +$10.65 | 1.23 |
| HYPE | 58 | 43.1% | +$488 | +0.69 | -7.0% | +$8.41 | 1.21 |
| **Combined** | **156** | **35.9%** | **-$962** | — | — | **-$6.16** | — |

Fees: BTC $584, ETH $360, HYPE $283 (total $1,227).
Exits: 139 stop / 17 signal — the opposite-divergence exit
fires more here than in the pattern strategies, but the stop
still dominates.

## Verdict: loser

-$962 across 156 trades. ETH and HYPE are both mildly green
(PF 1.21–1.23), but BTC loses -$1,908 with a 29.1% win rate and
Sharpe -3.09 — the worst single leg in this batch — and that
one leg erases both green legs twice over. A divergence signal
that fails this badly on the most liquid coin is not a
tradeable edge.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
