# Laguerre RSI (John Ehlers) — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
2026-03-14 00:00 UTC → 2026-10-19 13:00 UTC (5,247 bars BTC/ETH; 5,245 HYPE).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=60 bars.

**Implementation note (important):** the first implementation read the
source as running cumulative sums, `LRSI = cumup/(cumup+cumdn)`. That
ratio converges to the long-run up-move fraction and stops moving --
it produced 1 trade in 7 months. Re-reading the source page directly
(2026-10-19) shows the formula is explicitly per-bar: `UP = CU - CU_old`
(or 0), `DN = CU_old - CU` (or 0), `LRSI = UP/(UP+DN)`, with 0/0 holding
the previous value. The shipped implementation follows the source
literally. Consequence: `lrsi` only takes values {0, 0.5, 1} -- it is the
sign of the Laguerre-filtered momentum, so the 0.2/0.8/0.5 signal levels
act as direction-flip triggers (enter on the first up-bar of CU after a
fall, exit on the first down-bar).

## Results (shipped config: gamma=0.5, long on cross up through 0.2 /
short on cross down through 0.8, exits at the 0.5 centerline, 2xATR stop,
50-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 704 | 23.3% | -$6,631 | -65.9% | -4.53 | -68.1% | -$9.42 | 0.63 |
| ETH | 744 | 24.9% | -$5,785 | -57.9% | -3.54 | -60.6% | -$7.78 | 0.68 |
| HYPE | 621 | 31.2% | -$1,048 | -10.0% | -0.34 | -28.5% | -$1.69 | 0.94 |
| **Combined** | **2,069** | **26.3%** | **-$13,464** | — | — | — | -$6.51 | — |

## Verdict: clear loser

The per-bar Laguerre RSI flips sign constantly on 1h crypto -- 600-750
trades per coin over 7 months -- and each flip pays 0.055% round-trip.
Fees alone ($2,607-$4,754 per coin) explain most of the damage, but the
gross edge is negative too (profit factor 0.63-0.68 on BTC/ETH): buying
the first up-tick of a 0.5-gamma Laguerre filter after a down move is
not a reversal edge on this timeframe, it is noise-trading with a
smoother. HYPE loses least only because it trends harder (fewer flips).
Combined -$13,464 on 2,069 trades. This is an honest NO-GO as specified;
the indicator's published formula does not survive 1h crypto costs.

## Calibration note

Gamma sweep 0.3/0.5/0.7 in CALIBRATION.md: higher gamma (faster filter)
trades less and loses less, but no gamma turns BTC or ETH positive.
The shipped gamma=0.5 is kept as specified.

## Mechanism

L0..L3 Laguerre recurrences (gamma=0.5) on close, CU = mean of the four;
per-bar UP = max(CU-CU_prev, 0), DN = -min(CU-CU_prev, 0);
lrsi = UP/(UP+DN) in {0, 0.5, 1} (0/0 holds the previous value). Long
entries on lrsi crossing up through 0.2 (CU turns up after falling),
short on crossing down through 0.8; long exits on cross below 0.5,
short exits on cross above 0.5. 2xATR hard stop, no trailing/target (the
centerline exit manages the trade), 50-bar max hold.

Source: StockSharp docs, Laguerre RSI (Ehlers) —
https://doc.stocksharp.com/en/topics/api/indicators/list_of_indicators/laguerre_rsi

## Limitations

- Single 7-month crypto window; no bull-market or multi-year sample.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs idealized signal-bar entry; on a flip-every-
  bar system the one-bar delay is a first-order effect.
- The 0/0 -> previous-value rule seeds the first bar at 0.5; irrelevant
  after warmup.
- 50-bar max hold rarely binds (median hold is a few bars by construction).
