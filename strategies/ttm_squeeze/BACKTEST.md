# TTM Squeeze — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-09
(~5,000 bars each; API caps history at 5,000 candles/request).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation; 1h-bar holds keep it second-order).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: BB(20,2) vs KC(20-EMA, 1.5xATR14), >=5-bar squeeze, 12-bar momentum slope)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 64 | 34.4% | -$1,325 | -13.2% | -2.87 | -14.7% | -$20.70 | 0.41 |
| ETH | 77 | 31.2% | -$1,675 | -16.8% | -3.42 | -17.5% | -$21.75 | 0.38 |
| HYPE | 46 | 34.8% | -$680 | -6.8% | -2.10 | -9.0% | -$14.79 | 0.57 |
| **Combined** | **187** | **33.2%** | **-$3,680** | — | — | — | -$19.68 | — |

## Verdict: LOSER

Negative on all three coins with deeply negative Sharpe. The squeeze-release
mechanism as parameterized fires into chop: the 12-bar momentum slope is a
lagging direction filter that is still pointing the old way when the
expansion reverses, and the 2-bar momentum-fade exit bleeds on every
whipsaw. Fees ($1.7k combined) are material but not the story — profit
factor 0.38-0.57 means the gross edge is absent.

## Calibration note

Shipped exactly the specified parameters (BB 20/2.0, Keltner 20-EMA /
1.5xATR(14), >=5 squeeze bars, 12-bar regression-slope momentum, fade exit
after 2 consecutive against-momentum bars, 2xATR stop, 48-bar max hold, no
trailing/target) — no sweep was run because the spec was explicit and the
failure is structural, not parametric. What I verified instead: the release
bar is genuinely the first non-squeeze bar after a >=5-bar run (unit test),
and indicators are lookahead-free by truncation test. What didn't survive
contact with data: the momentum-slope direction filter. On 1h crypto bars
the slope is rising into the release bar on moves that immediately mean-
revert; Carter's original setup is a daily/options-volatility play where
the expansion has room to run, and the 1h port inherits none of that room.

## Mechanism

Volatility compression (BB inside KC) -> release trade in the direction of
the 12-bar linear-regression slope of (close - typical price). Exit on 2
consecutive momentum-fade bars against the position, 2xATR hard stop,
48-bar max hold.

Source: TTM Squeeze research (dexwilder/algo-lab) + Carter, Mastering the Trade Ch.11 —
https://github.com/dexwilder/algo-lab/blob/HEAD/research/volatility_expansion_strategy_research.md

## Limitations

- Single 7-month, choppy-to-bearish crypto window; no bull-market sample.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs idealized breakout entry.
- No parameter sweep attempted; a daily-bar variant was not tested.
