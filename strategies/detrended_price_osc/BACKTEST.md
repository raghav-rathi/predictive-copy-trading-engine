# Detrended Price Oscillator — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-46 window ms `[1773525600000, 1795615200000)`
(2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC exclusive, last
bar 13:00 UTC): 6,136 bars BTC/ETH, 6,134 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=35 bars.

## Results (shipped config: DPO(20) = close − SMA(20) shifted
back 11 bars, long on DPO crossing above 0, short on crossing
below 0, exit on the opposite cross, 2xATR stop, 3xATR trail,
60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 462 | 21.0% | -$5,087 | -49.7% | -3.24 | -53.8% | -$11.01 | 0.65 |
| ETH | 482 | 21.2% | -$3,218 | -31.0% | -1.63 | -45.3% | -$6.68 | 0.80 |
| HYPE | 454 | 23.6% | -$644 | -3.1% | -0.01 | -27.0% | -$1.42 | 0.96 |
| **Combined** | **1,398** | **21.9%** | **-$8,949** | — | **-2.06** | **-34.7%** | **-$6.40** | **0.81** |

Fees: BTC $3,644, ETH $3,641, HYPE $2,322 (total $9,608).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL. Combined start $30,000,
end $21,620. Exits: BTC 258 signal / 200 stop / 4 max-hold;
ETH 281 / 200 / 1; HYPE 268 / 181 / 5.

## Verdict: a loser on every coin — the zero-line cross is a lagging coin flip

Combined -$8,949 on 1,398 trades, win rate 21.0–23.6% —
the lowest win rate in this batch. The DPO is a cycle ruler,
not a signal: the zero-line cross fires only after price has
already moved well past the displaced average, so entries
are systematically late, and 200 of 462 BTC trades (43%)
end on the hard stop rather than the signal. HYPE is nearly
breakeven (-3.1%, Sharpe -0.01, PF 0.96) and still negative;
BTC loses half its account (-49.7%, Sharpe -3.24, MaxDD
-53.8%). There is no coin, no sub-period, no reading in
which the shipped config works on this window — which is
exactly what StockCharts warns when it says DPO "is not
designed for momentum signals."

## Calibration note

Shipped the specified DPO(20). A 10/20/40 period sweep on
this batch-46 window is in CALIBRATION.md: 10 gives
-$12,887 combined (2,046 trades), 40 gives -$5,874 (934
trades). Longer periods lose less, monotonically — but that
is mostly fewer trades and fewer fees, and 40 is still
-$5,874 with a 22–26% win rate. No in-sample adoption; the
shipped config stays 20.

## Mechanism

DPO(20) = close − SMA(close, 20) shifted back 11 bars
(displacement = 20/2 + 1), i.e. DPO[i] = close[i] −
SMA20[i − 11]. This is the causal, real-time reading: the
SMA as it stood 11 bars ago, subtracted from the current
close. It is NOT StockCharts' centered plotting convention
(price at a bar minus the SMA ending 11 bars in the future),
which uses future data. Long = DPO crosses above 0; short =
DPO crosses below 0; exit on the opposite cross. The harness
2xATR hard stop / 3xATR chandelier trail sit behind the
cross as a safety net for gap-through moves; 60-bar max hold.

Source: StockCharts ChartSchool, Detrended Price Oscillator
(DPO) —
https://chartschool.stockcharts.com/~gitbook/pdf?page=prVTFcIEDZPUBw709AIs&only=yes&limit=100
(the ChartSchool DPO article as returned by web search
2026-11-25; the article confirms the 20-period default, the
20/2 + 1 = 11 displacement, and that DPO "is not designed
for momentum signals"). The MetaStock "Technical Analysis
from A to Z" formula — "subtract the moving average
(n/2)+1 days ago from the closing price" — is the same
causal reading implemented here.

## Limitations

- Single ~8.4-month crypto window; 1,398 trades — the failure
  is consistent across all three coins, not a sample-size
  artefact.
- The zero-line cross is lagging by construction (the
  displaced average trails price by 11 bars), so entries
  chase moves that are already underway; 43% of BTC trades
  end on the hard stop.
- The calibration sweep improves monotonically with longer
  periods (10 → -$12,887, 20 → -$8,949, 40 → -$5,874) —
  but that is mostly trade-count/fees falling, and 40 is
  still a clear loser, so the "right" period is not
  identifiable from this window and adopting 40 would be
  in-sample selection on a trend that never reaches
  breakeven.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped DPO period on this window.
