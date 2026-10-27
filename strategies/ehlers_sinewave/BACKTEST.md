# Ehlers SineWave — Backtest

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
| BTC | 1360 | 40.5% | $-8,712 | -10.22 | -87.1% | $-6.41 | 0.56 |
| ETH | 1372 | 44.6% | $-7,851 | -7.65 | -80.0% | $-5.72 | 0.64 |
| HYPE | 1357 | 47.5% | $-6,399 | -5.49 | -65.3% | $-4.72 | 0.73 |
| **Combined** | **4089** | — | **$-22,962** | — | — | — | — |

Fees total: $17,238.

## Verdict

Loser — worst churn in the batch. The sine/lead-sine cross fires ~4,100 times on 1h bars; the Ehlers cycle-mode advantage does not survive hourly crypto, and the causal lead approximation tracks noise, not turning points.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Parameters fixed a priori; never tune the shipped parameters on
  this window.
- The causal lead (sine + half its 3-bar slope) is an approximation of Ehlers' Lead Sine, not the MESA phasor itself; a full dominant-cycle implementation might behave differently, but the cross frequency alone kills this version at 0.11% round-trip.
