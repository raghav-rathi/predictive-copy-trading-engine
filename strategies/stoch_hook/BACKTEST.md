# Stochastic Hook / Anti — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-09
(~5,000 bars each; API caps history at 5,000 candles/request).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation; 1h-bar holds keep it second-order).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: rawK(7), slowK=SMA10, trig=SMA4, EMA50 bias, 2xATR stop)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 301 | 30.2% | -$3,836 | -38.4% | -3.51 | -39.7% | -$12.74 | 0.62 |
| ETH | 271 | 30.3% | -$2,963 | -29.7% | -2.90 | -32.4% | -$10.93 | 0.67 |
| HYPE | 279 | 35.1% | -$2,601 | -26.0% | -2.86 | -26.7% | -$9.32 | 0.71 |
| **Combined** | **851** | **31.8%** | **-$9,400** | — | — | — | -$11.05 | — |

## Verdict: LOSER

Consistently negative on all three coins with a ~30% win rate. The hook
cross fires constantly on 1h bars (851 trades) — slowK(10)/trigger(4) on
hourly data whipsaws through every minor pullback, and the EMA50 bias
filter is too slow to keep the entries on the right side of the actual
swing. The cross-against exit then guarantees the trade is held through
the adverse excursion and exited near the worst point.

## Calibration note

Shipped the specified parameters exactly (rawK 7, slowK SMA-10, trigger
SMA-4, EMA50 trend bias, cross-against exit, 2xATR stop, 48-bar max hold)
with no sweep — the failure is the signal rate and the exit logic, not a
parameter choice. Verified in tests: hooks fire only with the EMA50 bias
on the correct side, crosses are lookahead-free, flat 7-bar windows get a
neutral rawK of 50. What the backtest says: on 1h bars the stochastic hook
is a churn machine. Raschke's Anti is a daily pattern where a hook is a
rare, tradeable event; compressed to 1h, "slowK crosses its trigger" is
background noise. A slower stochastic (e.g. 14/3/3 on 4h+ bars) or a
hook-depth filter (only trade hooks from <20 / >80 zones) are the obvious
next experiments — neither was run in this pass.

## Mechanism

Pullback entries with trend bias: slowK crosses its 4-bar trigger with
both slowK and rawK rising and close above EMA50 -> long (mirror for
shorts). Exit on the stochastic crossing against the position, 2xATR hard
stop, 48-bar max hold.

Source: Linda Raschke, Street Smarts (Anti) —
https://roboforex.com/blog/education/trading-strategies-that-were-a-revolution-three-strategies-of-linda-raschke/

## Limitations

- Single 7-month, choppy window; daily/4h variants untested.
- Funding unmodeled.
- Next-bar-open execution vs idealized hook-close entry.
- No hook-depth (overbought/oversold zone) filter in the shipped version.
