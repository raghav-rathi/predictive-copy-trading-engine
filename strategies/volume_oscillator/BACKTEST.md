# Volume Oscillator — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`): BTC/ETH 5,440 bars,
2026-03-14 22:00 UTC → 2026-10-27 13:00 UTC; HYPE 5,438 bars.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop,
3x leverage cap, $10k start, long/short.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 286 | 34.3% | $-902 | -0.42 | -22.7% | $-3.15 | 0.93 |
| ETH | 282 | 35.1% | $590 | 0.48 | -16.3% | $2.09 | 1.05 |
| HYPE | 278 | 35.6% | $323 | 0.35 | -19.4% | $1.16 | 1.03 |
| **Combined** | **846** | — | **$10** | — | — | — | — |

Fees total: $7,158.

## Verdict

Flat — +$10 combined on 846 trades is noise (expectancy $0.01/trade). Volume flow at 1h granularity carries no directional edge here.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
- The 5/10 volume windows are the standard short/long pair; the flat result is a finding, not a near-miss — no parameter rescue is claimed.
