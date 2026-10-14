# Chaikin Money Flow — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-14
(BTC 5,001 bars; ETH 5,001; HYPE 5,002).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: CMF(21) zero-cross + 200-bar SMA price regime
filter, exit on opposite cross, 2xATR stop, 3xATR trail, 240-bar max
hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 295 | 27.8% | −$4,923 | −49.2% | −5.73 | −49.4% | −$16.69 | 0.44 |
| ETH | 279 | 29.0% | −$2,050 | −20.5% | −1.85 | −24.2% | −$7.67 | 0.75 |
| HYPE | 237 | 31.2% | +$315 | +3.2% | +0.36 | −10.5% | +$1.02 | 1.03 |
| **Combined** | **811** | **29.2%** | **−$6,658** | — | — | — | −$8.21 | — |

## Verdict: LOSER (weak mixed — HYPE barely positive)

−$6,658 combined; BTC is a disaster (PF 0.44, −49.2%). The money-flow
zero cross is too slow to matter on 1h: by the time 21 bars of CLV
accumulate into a cross, the move that created the flow is over, and
the 200-bar regime filter just keeps the system long into distribution
tops. HYPE scrapes +3.2% — noise-level, not an edge (Sharpe 0.36 over
237 trades). Not worth a rescue in this form.

## Calibration note

Indicators verified: CMF matches the independent sum(MFV)/sum(V)
recomputation exactly; bounded ±1 confirmed; flat-bar division guard
tested; truncation test proves lookahead-freedom. Mechanism quirk: on
perps, "volume" is contract turnover, not share accumulation — the
accumulation/distribution story CMF was built for doesn't map cleanly.
If revisited, shorten the window toward 9–13 bars so the cross can
fire inside the move, and drop the 200-bar filter on 1h.
