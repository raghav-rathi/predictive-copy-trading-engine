# LSMA Slope — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-12
(~5,080 bars each).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: LSMA(21), 5-bar slope, price+slope alignment entries, slope-flip exits, 2xATR stop, 168-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 397 | 31.5% | -$3,200 | -30.9% | -1.52 | -48.0% | -$8.06 | 0.81 |
| ETH | 413 | 26.9% | -$5,397 | -54.0% | -3.41 | -56.4% | -$13.15 | 0.65 |
| HYPE | 348 | 37.9% | +$3,060 | +31.7% | 1.59 | -20.3% | +$8.79 | 1.17 |
| **Combined** | **1,158** | **31.9%** | **-$5,570** | — | — | — | -$4.81 | — |

## Verdict: MIXED

HYPE is a genuine winner (+31.7%, Sharpe 1.59, PF 1.17, 348 trades — the
largest per-coin sample in this batch), but BTC and ETH lose badly
(-31%/-54%, Sharpe -1.5/-3.4). A system that wins on one coin and loses
on two majors is not shippable as-is: combined -$5,570. The likely
mechanism story: HYPE's strong directional runs in this window reward a
slope-flip trend system, while BTC/ETH's choppier tape whipsaws the
21-bar LSMA slope and the slope-flip exit cuts winners at the first
counter-wobble. 397–413 trades per coin is too much churn for the edge.

## Calibration note

Shipped the classic LSMA(21)/5-bar slope without tuning. The length sweep
(14/21/34, see CALIBRATION.md) confirms 21 is the best of the three but
does not rescue BTC/ETH — the fix would need to be structural (a trend
regime filter so the system sits out chop), not parametric. What I
verified: LSMA is exact on a linear series (16.5 hand-check), leads the
SMA on trends as the theory claims, slope equals 5-bar rise exactly, and
indicators are lookahead-free by truncation test.

## Mechanism

LSMA(21) = endpoint of the least-squares regression line over the last 21
closes. Slope = LSMA - LSMA 5 bars ago. Long on fresh alignment of close
> LSMA and slope > 0; short mirrored; exit on slope flip. 2xATR hard
stop, no trailing/target, 168-bar max hold.

Source: Least Squares Moving Average — standard TA definition —
https://www.updata.co.uk/technical-analysis-glossary

## Limitations

- Single 7-month window; HYPE's win rides that coin's trend regime and may not persist.
- 348–413 trades/coin: fees ($3,540 BTC) eat a large share of gross edge.
- Funding unmodeled.
