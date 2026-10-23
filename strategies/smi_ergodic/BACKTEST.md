# SMI Ergodic — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-14
(BTC 5,001 bars; ETH 5,001; HYPE 5,002).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: Blau SMI = 100·doubleEMA(d,20,5)/doubleEMA(|d|,20,5),
5-bar signal, cross entries with zero-line regime filter, exit on opposite
cross, 2xATR stop, 3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 322 | 25.8% | −$4,150 | −41.5% | −4.67 | −41.8% | −$12.89 | 0.55 |
| ETH | 305 | 25.6% | −$1,771 | −17.7% | −1.34 | −28.7% | −$6.10 | 0.78 |
| HYPE | 289 | 31.1% | −$1,815 | −18.2% | −1.92 | −21.7% | −$6.28 | 0.78 |
| **Combined** | **916** | **27.4%** | **−$7,736** | — | — | — | −$8.45 | — |

## Verdict: LOSER (killed)

Loses on all three coins, −$7,736 combined — the worst expectancy in
this batch after Qstick. The double smoothing that makes SMI "ergodic"
also makes it late: by the time SMI crosses its signal with the
zero-line filter satisfied, the 1h move is mostly done, and the exit on
the opposite cross gives back what the stop didn't take. The zero-line
regime filter didn't save it; it just concentrated entries into
already-extended moves. No parameter rescue attempted — the failure is
structural (lag), not tuning.

## Calibration note

Indicators verified: independent double-EMA recomputation matches to
1e-9; boundedness ±100 confirmed; truncation test proves
lookahead-freedom. Mechanism quirk worth knowing: the zero-line filter
plus signal cross is really two lags stacked — the cross is already a
lagging trigger, and requiring SMI>0/<0 delays it further into the
move. If anyone revisits this, the only direction with a chance is
dropping the regime filter and trading the raw signal cross with a
tighter stop, accepting more whipsaw for earlier entries.
