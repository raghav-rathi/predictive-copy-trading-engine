# Stochastic + MACD Combo — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-46 window ms `[1773525600000, 1795615200000)`
(2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC exclusive, last
bar 13:00 UTC): 6,136 bars BTC/ETH, 6,134 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=40 bars.

## Results (shipped config: Fast Stochastic %K(14)/%D(3),
MACD(12,26,9); long on an oversold %K cross up with MACD
histogram > 0, short on an overbought %K cross down with
histogram < 0, exit on the opposite Stochastic cross or a
histogram sign flip, 2xATR stop, 3xATR trail, 60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 24 | 41.7% | -$304 | -3.0% | -1.28 | -4.3% | -$12.65 | 0.62 |
| ETH | 26 | 30.8% | -$606 | -6.1% | -2.33 | -7.9% | -$23.30 | 0.32 |
| HYPE | 23 | 21.7% | -$609 | -6.1% | -2.26 | -7.2% | -$26.47 | 0.34 |
| **Combined** | **73** | **31.5%** | **-$1,518** | **-5.1%** | **-3.25** | **-6.1%** | **-$20.80** | **0.42** |

Fees: BTC $292, ETH $192, HYPE $112 (total $596).
Exits: BTC signal 21 / stop 3; ETH signal 21 / stop 5;
HYPE signal 17 / stop 6. Net % is the final-equity return
(it includes the mark-to-market of any position still open at
the window end); Net $ is the sum of closed-trade PnL.

## Verdict: a loser — the dual confirmation is so strict it
barely trades, and the trades it does take lose badly

Combined -$1,518 on just 73 trades — the strictest filter in
this batch. Requiring an oversold/overbought Stochastic cross
AND a MACD histogram of the right sign means the two
indicators almost never agree on 1h crypto: they disagree
because the Stochastic is fast and mean-reverting while the
MACD histogram is slow and trend-following, so the moments
both point the same way are exactly the moments the move is
already over. When it does trade, it loses with conviction:
profit factor 0.32–0.62, expectancy -$12.65 to -$26.47 per
trade, and the combined Sharpe is -3.25 — the worst Sharpe
per dollar lost in the batch, because the equity curve grinds
down with almost no winning offset. Only 73 trades in 8.4
months, and 68.5% of them lose. The drawdowns are small
(-4.3% to -7.9%) only because the system is mostly flat,
not because it manages risk well.

## Calibration note

Shipped the specified %K period 14. A 7/14/21 %K-period
sweep on this batch-46 window is in CALIBRATION.md: 7 is
the least bad combined (-$1,310, 126 trades) with a near-
breakeven HYPE read (+$18) — but that is an in-sample
observation on a knob that only changes how often the
Stochastic fires, and every value is still a combined loser
with PF 0.42–0.59. The 14 config was fixed before any
backtest was run; no in-sample adoption — the shipped config
stays 14 and the verdict stays: loser.

## Mechanism

Fast Stochastic (George C. Lane, StockCharts ChartSchool):
%K = 100 × (close − lowest low(14)) / (highest high(14) −
lowest low(14)); %D = SMA(%K, 3). MACD(12,26,9) histogram
from `strategies/base.py`. Long = %K crosses above %D while
%K < 30 AND MACD histogram > 0; short = %K crosses below %D
while %K > 70 AND MACD histogram < 0; exit on the opposite
Stochastic cross OR the MACD histogram flipping sign. A zero
14-bar high-low range reads %K = 50 (neutral). The harness
2xATR hard stop / 3xATR chandelier trail sit behind the
signal logic as a safety net for gap-through moves; 60-bar
max hold.

Source: StockCharts ChartSchool, "Stochastic Oscillator (Fast,
Slow, and Full)" —
https://chartschool.stockcharts.com/~gitbook/pdf?page=QVB5cA3WHQlQdjo1YmxN&only=yes&limit=100
(verified via search 2026-11-25; confirms %K over 14 periods,
%D = 3-period SMA of %K, and the fast/slow/full versions).
MACD(12,26,9) is the standard MACD from `strategies/base.py`.

## Limitations

- Single ~8.4-month crypto window; only 73 trades — the
  failure is consistent (PF ≤ 0.62 on every coin) but the
  sample is small, so the per-coin numbers are noisy.
- The dual filter is the problem: two indicators with
  opposite characters (fast mean-reversion vs slow trend)
  agree rarely, and when they do the edge is already gone.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped %K period on this window.
