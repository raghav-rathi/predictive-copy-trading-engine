# fibonacci_extension — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`): BTC/ETH 5,384 bars,
2026-03-14 22:00 UTC → 2026-10-25 00:00 UTC; HYPE 5,382 bars,
2026-03-15 00:00 UTC → 2026-10-25 00:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop (VCP: 1.5xATR),
3x leverage cap, $10k start, long/short except VCP (long only).

## Results (shipped config: SMA50 trend + turn from 38.2-61.8% zone; 50-bar range)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 159 | 20.1% | $-2,330 | -2.31 | -24.1% | $-14.65 | 0.62 |
| ETH | 191 | 21.5% | $-2,028 | -1.84 | -23.2% | $-10.62 | 0.71 |
| HYPE | 141 | 22.0% | $-1,752 | -2.33 | -18.1% | $-12.43 | 0.60 |
| **Combined** | **491** | — | **$-6,110** | — | — | — | — |

Fees total: $3,911.

## Verdict

Loser — retracement turns lose on every coin with win rates ~21%.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
